from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


@dataclass
class COTLayerResult:
    layer_name: str
    input_data: Any
    output_data: Any
    reasoning_steps: List[str] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class COTResult:
    request_id: str
    agent_name: str
    layers: List[COTLayerResult] = field(default_factory=list)
    final_output: Any = None
    is_complete: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "agent_name": self.agent_name,
            "layers": [
                {
                    "layer_name": l.layer_name,
                    "output_data": l.output_data,
                    "reasoning_steps": l.reasoning_steps,
                    "confidence": l.confidence,
                    "timestamp": l.timestamp.isoformat()
                }
                for l in self.layers
            ],
            "final_output": self.final_output,
            "is_complete": self.is_complete,
            "error": self.error
        }


class BaseCOTAgent(ABC):
    def __init__(self, name: str, enable_debug: bool = False):
        self.name = name
        self.enable_debug = enable_debug
        self.reasoning_history: List[COTResult] = []

    def create_cot_result(self) -> COTResult:
        return COTResult(
            request_id=str(uuid.uuid4()),
            agent_name=self.name
        )

    @abstractmethod
    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        pass

    @abstractmethod
    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        pass

    @abstractmethod
    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        pass

    @abstractmethod
    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        pass

    async def process_with_cot(self, input_data: dict) -> COTResult:
        cot_result = self.create_cot_result()

        try:
            layer1_output = await self.intent_understanding_layer(input_data, cot_result)
            cot_result.layers.append(layer1_output)

            layer2_output = await self.knowledge_retrieval_layer(layer1_output.output_data, cot_result)
            cot_result.layers.append(layer2_output)

            layer3_output = await self.reasoning_decision_layer(layer2_output.output_data, cot_result)
            cot_result.layers.append(layer3_output)

            layer4_output = await self.response_generation_layer(layer3_output.output_data, cot_result)
            cot_result.layers.append(layer4_output)

            cot_result.final_output = layer4_output.output_data
            cot_result.is_complete = True

            self.reasoning_history.append(cot_result)

        except Exception as e:
            cot_result.error = str(e)
            cot_result.is_complete = False

        return cot_result

    def get_reasoning_history(self, request_id: Optional[str] = None) -> List[COTResult]:
        if request_id:
            return [r for r in self.reasoning_history if r.request_id == request_id]
        return self.reasoning_history

    def clear_history(self):
        self.reasoning_history = []
