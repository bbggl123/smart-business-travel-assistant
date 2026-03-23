from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import json


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        **kwargs
    ) -> str:
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> AsyncIterator[str]:
        pass


class LLMResponse:
    def __init__(self, content: str, usage: Optional[dict] = None):
        self.content = content
        self.usage = usage or {}

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "usage": self.usage
        }


def parse_sse_stream(stream_data: str) -> AsyncIterator[str]:
    for line in stream_data.split("\n"):
        line = line.strip()
        if not line or not line.startswith("data:"):
            continue

        data = line[5:].strip()
        if data == "[DONE]":
            break

        try:
            json_data = json.loads(data)
            if "choices" in json_data:
                delta = json_data["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]
        except json.JSONDecodeError:
            continue
