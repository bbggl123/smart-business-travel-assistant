from typing import AsyncIterator, Optional
from .providers.base import BaseLLMProvider, LLMResponse
from .providers.zidongtaichu import ZidongtaichuProvider, ZidongtaichuProviderSync
from app.config import settings
from app.utils.logger import logger


class LLMWrapper:
    def __init__(self):
        self.provider: BaseLLMProvider = ZidongtaichuProvider()
        logger.info("LLM Gateway initialized with Zidongtaichu provider")

    async def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        **kwargs
    ) -> str:
        return await self.provider.chat(messages, stream=stream, **kwargs)

    async def chat_stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> AsyncIterator[str]:
        async for chunk in self.provider.chat_stream(messages, **kwargs):
            yield chunk

    async def chat_no_stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> str:
        chunks = []
        async for chunk in self.provider.chat_stream(messages, **kwargs):
            chunks.append(chunk)
        return "".join(chunks)


llm_gateway = LLMWrapper()


async def get_llm() -> LLMWrapper:
    return llm_gateway
