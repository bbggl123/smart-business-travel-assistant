from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from app.cot.base import COTLayerResult, COTResult
from app.cot.engine import COTEngine, COTPromptEngine
from app.utils.logger import logger
import json


class BaseAgent(ABC):
    def __init__(self, name: str, enable_cot: bool = True):
        self.name = name
        self.enable_cot = enable_cot
        self.cot_engine = COTEngine(enable_debug=False) if enable_cot else None
        self.prompt_engine = COTPromptEngine()
        self.logger = logger

    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        pass

    async def run(self, input_data: dict) -> dict:
        self.logger.info(f"{self.name} processing input: {input_data}")
        try:
            if self.enable_cot:
                result = await self.process_with_cot(input_data)
            else:
                result = await self.process(input_data)
            self.logger.info(f"{self.name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"{self.name} error: {str(e)}")
            raise

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        raise NotImplementedError

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        raise NotImplementedError

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        raise NotImplementedError

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        raise NotImplementedError

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"{self.name}_{datetime.now().timestamp()}",
            agent_name=self.name
        )

        try:
            layer1 = await self.intent_understanding_layer(input_data, cot_result)
            cot_result.layers.append(layer1)

            layer2 = await self.knowledge_retrieval_layer(layer1.output_data, cot_result)
            cot_result.layers.append(layer2)

            layer3 = await self.reasoning_decision_layer(layer2.output_data, cot_result)
            cot_result.layers.append(layer3)

            layer4 = await self.response_generation_layer(layer3.output_data, cot_result)
            cot_result.layers.append(layer4)

            cot_result.final_output = layer4.output_data
            cot_result.is_complete = True

            return {
                "result": layer4.output_data,
                "cot": cot_result.to_dict()
            }
        except Exception as e:
            self.logger.error(f"{self.name} COT error: {str(e)}")
            return {
                "result": await self.process(input_data),
                "cot": cot_result.to_dict(),
                "error": str(e)
            }

    async def call_llm(self, prompt: str) -> str:
        from app.llm.gateway import llm_gateway as gateway
        messages = [
            {"role": "system", "content": "你是一个专业的商旅助手，擅长分析用户的出差需求。"},
            {"role": "user", "content": prompt}
        ]
        return await gateway.chat_no_stream(messages)

    def parse_llm_json_response(self, response: str, fallback: dict = None) -> dict:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            if fallback:
                return fallback
            return {"error": "Failed to parse LLM response"}
