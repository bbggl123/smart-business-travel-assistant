from typing import Optional, List, Dict, Any
from supabase import Client
from app.utils.logger import logger
from datetime import datetime


class StorageService:
    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def save_trip(self, trip_data: dict) -> dict:
        try:
            trip_data["created_at"] = datetime.now().isoformat()
            trip_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("trips").insert(trip_data).execute()
            logger.info(f"Saved trip: {trip_data.get('id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving trip: {e}")
            return {"status": "error", "message": str(e)}

    async def get_trip(self, trip_id: str) -> dict:
        try:
            result = self.client.table("trips").select("*").eq("id", trip_id).execute()
            if result.data:
                return {"status": "success", "data": result.data[0]}
            return {"status": "error", "message": "Trip not found"}
        except Exception as e:
            logger.error(f"Error getting trip: {e}")
            return {"status": "error", "message": str(e)}

    async def update_trip(self, trip_id: str, trip_data: dict) -> dict:
        try:
            trip_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("trips").update(trip_data).eq("id", trip_id).execute()
            logger.info(f"Updated trip: {trip_id}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error updating trip: {e}")
            return {"status": "error", "message": str(e)}

    async def list_trips(self, user_id: str = None, status: str = None) -> dict:
        try:
            query = self.client.table("trips").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
            result = query.execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Error listing trips: {e}")
            return {"status": "error", "message": str(e)}

    async def save_booking(self, booking_data: dict) -> dict:
        try:
            booking_data["created_at"] = datetime.now().isoformat()
            booking_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("bookings").insert(booking_data).execute()
            logger.info(f"Saved booking: {booking_data.get('id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving booking: {e}")
            return {"status": "error", "message": str(e)}

    async def get_booking(self, booking_id: str) -> dict:
        try:
            result = self.client.table("bookings").select("*").eq("id", booking_id).execute()
            if result.data:
                return {"status": "success", "data": result.data[0]}
            return {"status": "error", "message": "Booking not found"}
        except Exception as e:
            logger.error(f"Error getting booking: {e}")
            return {"status": "error", "message": str(e)}

    async def update_booking_status(self, booking_id: str, status: str) -> dict:
        try:
            result = self.client.table("bookings").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", booking_id).execute()
            logger.info(f"Updated booking status: {booking_id} -> {status}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error updating booking status: {e}")
            return {"status": "error", "message": str(e)}

    async def list_bookings(self, trip_id: str = None, user_id: str = None) -> dict:
        try:
            query = self.client.table("bookings").select("*")
            if trip_id:
                query = query.eq("trip_id", trip_id)
            if user_id:
                query = query.eq("user_id", user_id)
            result = query.execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Error listing bookings: {e}")
            return {"status": "error", "message": str(e)}

    async def save_approval_form(self, approval_data: dict) -> dict:
        try:
            approval_data["created_at"] = datetime.now().isoformat()
            approval_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("approval_forms").insert(approval_data).execute()
            logger.info(f"Saved approval form: {approval_data.get('id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving approval form: {e}")
            return {"status": "error", "message": str(e)}

    async def get_approval_form(self, approval_id: str) -> dict:
        try:
            result = self.client.table("approval_forms").select("*").eq("id", approval_id).execute()
            if result.data:
                return {"status": "success", "data": result.data[0]}
            return {"status": "error", "message": "Approval form not found"}
        except Exception as e:
            logger.error(f"Error getting approval form: {e}")
            return {"status": "error", "message": str(e)}

    async def save_invoice(self, invoice_data: dict) -> dict:
        try:
            invoice_data["created_at"] = datetime.now().isoformat()
            invoice_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("invoices").insert(invoice_data).execute()
            logger.info(f"Saved invoice: {invoice_data.get('id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            return {"status": "error", "message": str(e)}

    async def get_invoice(self, invoice_id: str) -> dict:
        try:
            result = self.client.table("invoices").select("*").eq("id", invoice_id).execute()
            if result.data:
                return {"status": "success", "data": result.data[0]}
            return {"status": "error", "message": "Invoice not found"}
        except Exception as e:
            logger.error(f"Error getting invoice: {e}")
            return {"status": "error", "message": str(e)}

    async def list_invoices(self, trip_id: str = None, user_id: str = None) -> dict:
        try:
            query = self.client.table("invoices").select("*")
            if trip_id:
                query = query.eq("trip_id", trip_id)
            if user_id:
                query = query.eq("user_id", user_id)
            result = query.execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            return {"status": "error", "message": str(e)}

    async def save_conversation(self, conversation_data: dict) -> dict:
        try:
            conversation_data["created_at"] = datetime.now().isoformat()
            conversation_data["updated_at"] = datetime.now().isoformat()
            result = self.client.table("conversations").insert(conversation_data).execute()
            logger.info(f"Saved conversation: {conversation_data.get('id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return {"status": "error", "message": str(e)}

    async def get_conversation(self, conversation_id: str) -> dict:
        try:
            result = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
            if result.data:
                return {"status": "success", "data": result.data[0]}
            return {"status": "error", "message": "Conversation not found"}
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return {"status": "error", "message": str(e)}

    async def save_message(self, message_data: dict) -> dict:
        try:
            message_data["created_at"] = datetime.now().isoformat()
            result = self.client.table("messages").insert(message_data).execute()
            logger.info(f"Saved message for conversation: {message_data.get('conversation_id')}")
            return {"status": "success", "data": result.data[0] if result.data else None}
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return {"status": "error", "message": str(e)}

    async def get_messages(self, conversation_id: str) -> dict:
        try:
            result = self.client.table("messages").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at").execute()
            return {"status": "success", "data": result.data}
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {"status": "error", "message": str(e)}


class RedisCacheService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def set_session(self, session_id: str, session_data: dict, ttl: int = 3600) -> bool:
        try:
            key = f"session:{session_id}"
            import json
            await self.redis.setex(key, ttl, json.dumps(session_data))
            logger.info(f"Set session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting session: {e}")
            return False

    async def get_session(self, session_id: str) -> dict:
        try:
            key = f"session:{session_id}"
            import json
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        try:
            key = f"session:{session_id}"
            await self.redis.delete(key)
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    async def set_workflow_state(self, workflow_id: str, state: dict, ttl: int = 7200) -> bool:
        try:
            key = f"workflow:{workflow_id}"
            import json
            await self.redis.setex(key, ttl, json.dumps(state))
            logger.info(f"Set workflow state: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting workflow state: {e}")
            return False

    async def get_workflow_state(self, workflow_id: str) -> dict:
        try:
            key = f"workflow:{workflow_id}"
            import json
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting workflow state: {e}")
            return None

    async def publish_event(self, channel: str, event_data: dict) -> bool:
        try:
            import json
            await self.redis.publish(channel, json.dumps(event_data))
            logger.info(f"Published event to {channel}")
            return True
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

    async def set_agent_result(self, agent_id: str, result: dict, ttl: int = 300) -> bool:
        try:
            key = f"agent_result:{agent_id}"
            import json
            await self.redis.setex(key, ttl, json.dumps(result))
            logger.info(f"Set agent result: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting agent result: {e}")
            return False

    async def get_agent_result(self, agent_id: str) -> dict:
        try:
            key = f"agent_result:{agent_id}"
            import json
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting agent result: {e}")
            return None