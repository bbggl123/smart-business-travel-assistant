import httpx
from typing import AsyncIterator, Optional
from app.config import settings
from app.utils.logger import logger
from .base import BaseLLMProvider, LLMResponse, parse_sse_stream


class ZidongtaichuProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.zidongtaichu_api_key
        self.api_url = settings.zidongtaichu_api_url
        self.model = settings.zidongtaichu_model
        self.max_retries = 3
        self.timeout = 120.0

    async def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        temperature: float = 0.8,
        top_p: float = 0.9,
        max_tokens: int = 32768,
        **kwargs
    ) -> str:
        async for chunk in self.chat_stream(
            messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.8,
        top_p: float = 0.9,
        max_tokens: int = 32768,
        repetition_penalty: float = 1.0,
        **kwargs
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "repetition_penalty": repetition_penalty
        }

        logger.info(f"Calling Zidongtaichu API: {self.api_url}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                self.api_url,
                json=payload,
                headers=headers
            ) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    logger.error(f"API Error: {response.status_code} - {error_body.decode()}")
                    raise Exception(f"API Error: {response.status_code}")

                full_content = ""
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if data == "[DONE]":
                        break

                    try:
                        import json
                        json_data = json.loads(data)
                        if "choices" in json_data:
                            delta = json_data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_content += content
                                yield content
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error: {e}")
                        continue

                logger.info(f"Full response received, length: {len(full_content)}")


class ZidongtaichuProviderSync(BaseLLMProvider):
    def __init__(self):
        self.provider = ZidongtaichuProvider()

    async def chat(
        self,
        messages: list[dict],
        stream: bool = False,
        **kwargs
    ) -> str:
        if stream:
            chunks = []
            async for chunk in self.provider.chat_stream(messages, **kwargs):
                chunks.append(chunk)
            return "".join(chunks)
        else:
            chunks = []
            async for chunk in self.provider.chat_stream(messages, **kwargs):
                chunks.append(chunk)
            return "".join(chunks)

    async def chat_stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> AsyncIterator[str]:
        async for chunk in self.provider.chat_stream(messages, **kwargs):
            yield chunk
