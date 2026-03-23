import redis.asyncio as redis
import json
import uuid
from typing import Optional, List, Dict, Any, Callable
from app.config import settings
from app.utils.logger import logger


STREAMS_KEY_PREFIX = "streams:"
AGENT_QUEUE_PREFIX = "agents:queue:"


class RedisStreamsClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.consumer_groups: Dict[str, str] = {}

    async def connect(self):
        if self.redis is None:
            self.redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                decode_responses=False
            )
            logger.info("Redis Streams client connected")

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def xadd(self, stream_key: str, data: dict, maxlen: int = 1000) -> str:
        if not self.redis:
            await self.connect()

        message_id = "*"
        fields = {k: str(v).encode() if not isinstance(v, bytes) else v for k, v in data.items()}

        result = await self.redis.xadd(stream_key, fields, maxlen=maxlen)
        msg_id = result.decode() if isinstance(result, bytes) else result
        logger.debug(f"XADD {stream_key}: {msg_id}")
        return msg_id

    async def xread(
        self,
        streams: List[str],
        count: int = 10,
        block: int = 5000
    ) -> List[tuple]:
        if not self.redis:
            await self.connect()

        stream_keys = [STREAMS_KEY_PREFIX + s if not s.startswith(STREAMS_KEY_PREFIX) else s for s in streams]
        result = await self.redis.xread(stream_keys, count=count, block=block)

        parsed = []
        if result:
            for stream_name, messages in result:
                stream_name_str = stream_name.decode() if isinstance(stream_name, bytes) else stream_name
                parsed_messages = []
                for msg_id, fields in messages:
                    msg_id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                    parsed_fields = {}
                    for k, v in fields.items():
                        key = k.decode() if isinstance(k, bytes) else k
                        val = v.decode() if isinstance(v, bytes) else v
                        parsed_fields[key] = val
                    parsed_messages.append((msg_id_str, parsed_fields))
                parsed.append((stream_name_str, parsed_messages))

        return parsed

    async def xgroup_create(
        self,
        stream_key: str,
        group_name: str,
        start_id: str = "0",
        mkstream: bool = True
    ) -> bool:
        if not self.redis:
            await self.connect()

        full_key = STREAMS_KEY_PREFIX + stream_key if not stream_key.startswith(STREAMS_KEY_PREFIX) else stream_key

        try:
            await self.redis.xgroup_create(full_key, group_name, start_id, mkstream=mkstream)
            self.consumer_groups[f"{full_key}:{group_name}"] = full_key
            logger.info(f"Created consumer group: {group_name} for stream: {full_key}")
            return True
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.debug(f"Consumer group {group_name} already exists")
                return True
            raise e

    async def xreadgroup(
        self,
        stream_key: str,
        group_name: str,
        consumer_name: str,
        count: int = 10,
        block: int = 5000
    ) -> List[tuple]:
        if not self.redis:
            await self.connect()

        full_key = STREAMS_KEY_PREFIX + stream_key if not stream_key.startswith(STREAMS_KEY_PREFIX) else stream_key
        group_name_bytes = group_name.encode() if isinstance(group_name, str) else group_name
        consumer_name_bytes = consumer_name.encode() if isinstance(consumer_name, str) else consumer_name

        try:
            result = await self.redis.xreadgroup(
                full_key, group_name_bytes, consumer_name_bytes,
                count=count, block=block
            )
        except Exception as e:
            logger.error(f"XREADGROUP error: {e}")
            return []

        if not result:
            return []

        parsed = []
        for stream_name, messages in result:
            stream_name_str = stream_name.decode() if isinstance(stream_name, bytes) else stream_name
            parsed_messages = []
            for msg_id, fields in messages:
                msg_id_str = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                parsed_fields = {}
                for k, v in fields.items():
                    key = k.decode() if isinstance(k, bytes) else k
                    val = v.decode() if isinstance(v, bytes) else v
                    try:
                        parsed_fields[key] = json.loads(val)
                    except:
                        parsed_fields[key] = val
                parsed_messages.append((msg_id_str, parsed_fields))
            parsed.append((stream_name_str, parsed_messages))

        return parsed

    async def xack(self, stream_key: str, group_name: str, *message_ids) -> int:
        if not self.redis:
            await self.connect()

        full_key = STREAMS_KEY_PREFIX + stream_key if not stream_key.startswith(STREAMS_KEY_PREFIX) else stream_key
        return await self.redis.xack(full_key, group_name, *message_ids)

    async def xinfo_groups(self, stream_key: str) -> List[dict]:
        if not self.redis:
            await self.connect()

        full_key = STREAMS_KEY_PREFIX + stream_key if not stream_key.startswith(STREAMS_KEY_PREFIX) else stream_key
        try:
            groups = await self.redis.xinfo_groups(full_key)
            return [dict(g) for g in groups]
        except:
            return []

    async def get_pending(self, stream_key: str, group_name: str) -> List:
        if not self.redis:
            await self.connect()

        full_key = STREAMS_KEY_PREFIX + stream_key if not stream_key.startswith(STREAMS_KEY_PREFIX) else stream_key
        group_name_bytes = group_name.encode() if isinstance(group_name, str) else group_name

        try:
            pending = await self.redis.xpending(full_key, group_name_bytes)
            return pending if pending else []
        except:
            return []


class MessageQueueService:
    def __init__(self):
        self.client = RedisStreamsClient()
        self.handlers: Dict[str, Callable] = {}

    async def connect(self):
        await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    async def publish_message(
        self,
        target_agent: str,
        message: dict,
        stream_key: str = None
    ) -> str:
        if stream_key is None:
            stream_key = AGENT_QUEUE_PREFIX + target_agent

        message_data = {
            "msg_id": str(uuid.uuid4()),
            "target_agent": target_agent,
            "payload": json.dumps(message) if isinstance(message, dict) else str(message),
            "timestamp": str(uuid.uuid4())[:13]
        }

        msg_id = await self.client.xadd(stream_key, message_data)
        logger.info(f"Published message to {target_agent}: {message_data['msg_id']}")
        return msg_id

    async def broadcast_message(self, message: dict, exclude_agents: List[str] = None) -> List[str]:
        agent_queues = [
            "agents:queue:transportation",
            "agents:queue:hotel",
            "agents:queue:dining",
            "agents:queue:compliance",
            "agents:queue:approval",
            "agents:queue:invoice"
        ]

        msg_ids = []
        for queue in agent_queues:
            agent_name = queue.replace("agents:queue:", "")
            if exclude_agents and agent_name in exclude_agents:
                continue

            message_data = {
                "msg_id": str(uuid.uuid4()),
                "type": "broadcast",
                "payload": json.dumps(message) if isinstance(message, dict) else str(message),
                "timestamp": str(uuid.uuid4())[:13]
            }

            msg_id = await self.client.xadd(queue, message_data)
            msg_ids.append(msg_id)

        logger.info(f"Broadcast message to {len(msg_ids)} agents")
        return msg_ids

    async def register_handler(self, agent_name: str, handler: Callable):
        self.handlers[agent_name] = handler
        logger.info(f"Registered handler for agent: {agent_name}")

    async def start_consuming(self, agent_name: str, group_name: str, consumer_name: str):
        stream_key = AGENT_QUEUE_PREFIX + agent_name

        await self.client.xgroup_create(stream_key, group_name, mkstream=True)

        handler = self.handlers.get(agent_name)
        if not handler:
            logger.warning(f"No handler registered for agent: {agent_name}")
            return

        logger.info(f"Starting consumer for {agent_name} (group: {group_name}, consumer: {consumer_name})")

        while True:
            try:
                messages = await self.client.xreadgroup(
                    stream_key, group_name, consumer_name, count=5, block=3000
                )

                for stream_name, msgs in messages:
                    for msg_id, fields in msgs:
                        try:
                            payload = fields.get("payload", "{}")
                            message_data = json.loads(payload) if isinstance(payload, str) else payload

                            result = await handler(message_data)

                            await self.client.xack(stream_name.replace(STREAMS_KEY_PREFIX, ""), group_name, msg_id)

                            logger.debug(f"Processed message {msg_id} for {agent_name}")
                        except Exception as e:
                            logger.error(f"Error processing message {msg_id}: {e}")
            except Exception as e:
                logger.error(f"Consumer error for {agent_name}: {e}")
                import asyncio
                await asyncio.sleep(5)

    async def get_queue_info(self, stream_key: str) -> dict:
        groups = await self.client.xinfo_groups(stream_key)
        pending = []
        for group in groups:
            group_name = group.get("name", "").decode() if isinstance(group.get("name"), bytes) else group.get("name", "")
            pending_info = await self.client.get_pending(stream_key, group_name)
            pending.append({"group": group_name, "pending_count": len(pending_info)})

        return {
            "stream": stream_key,
            "groups": groups,
            "pending": pending
        }


_message_queue_service: Optional[MessageQueueService] = None


async def get_message_queue() -> MessageQueueService:
    global _message_queue_service
    if _message_queue_service is None:
        _message_queue_service = MessageQueueService()
        await _message_queue_service.connect()
    return _message_queue_service


async def close_message_queue():
    global _message_queue_service
    if _message_queue_service:
        await _message_queue_service.disconnect()
        _message_queue_service = None
