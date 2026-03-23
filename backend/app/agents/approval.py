from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from typing import Dict, List, Any
from app.utils.logger import logger
import json


class ApprovalAgent(BaseAgent):
    def __init__(self):
        super().__init__("ApprovalAgent")

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)

        action = input_data.get("action", "generate")
        if action == "generate":
            return await self._simple_generate(input_data)
        return {"status": "error", "message": f"Unknown action: {action}"}

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"approval_{id(input_data)}",
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
                **layer4.output_data,
                "cot": cot_result.to_dict()
            }
        except Exception as e:
            self.logger.error(f"ApprovalAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_generate(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        trip_data = input_data.get("trip_data", {})
        transport_data = input_data.get("transport", {})
        hotel_data = input_data.get("hotel", {})
        dining_data = input_data.get("dining", {})

        reasoning_steps = [
            f"接收行程数据汇总请求",
            f"行程信息: {trip_data.get('destination', '未知')}",
            f"交通数据: {'有' if transport_data else '无'}",
            f"酒店数据: {'有' if hotel_data else '无'}",
            f"餐饮数据: {'有' if dining_data else '无'}"
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "trip_data": trip_data,
                "transport_data": transport_data,
                "hotel_data": hotel_data,
                "dining_data": dining_data,
                "has_transport": bool(transport_data),
                "has_hotel": bool(hotel_data),
                "has_dining": bool(dining_data)
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        from app.cot.knowledge_base import knowledge_base

        trip_data = input_data.get("trip_data", {})
        user_level = trip_data.get("user_level", "基层员工")

        level_info = knowledge_base.retrieve_level_info(user_level)
        approval_chain = level_info.get("approval_chain", ["直属主管"])

        reasoning_steps = [
            f"检索用户职级: {user_level}",
            f"审批链: {' -> '.join(approval_chain)}",
            f"最大审批金额: {level_info.get('max_approval_amount', 5000)}元"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "approval_chain": approval_chain,
                "max_approval_amount": level_info.get("max_approval_amount", 5000),
                "user_level": user_level
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        transport_data = input_data.get("transport_data", {})
        hotel_data = input_data.get("hotel_data", {})
        dining_data = input_data.get("dining_data", {})

        transport_cost = self._extract_cost(transport_data, "transport")
        hotel_cost = self._extract_cost(hotel_data, "hotel")
        dining_cost = self._extract_cost(dining_data, "dining")

        total_cost = transport_cost + hotel_cost + dining_cost

        knowledge = input_data.get("knowledge_retrieval_output", {})
        max_amount = knowledge.get("max_approval_amount", 5000)

        needs_special_approval = total_cost > max_amount

        reasoning_steps = [
            f"计算各项费用",
            f"交通费用: {transport_cost}元",
            f"住宿费用: {hotel_cost}元",
            f"餐饮费用: {dining_cost}元",
            f"总费用: {total_cost}元",
            f"是否需要特殊审批: {'是' if needs_special_approval else '否'}"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "transport_cost": transport_cost,
                "hotel_cost": hotel_cost,
                "dining_cost": dining_cost,
                "total_cost": total_cost,
                "needs_special_approval": needs_special_approval,
                "approval_items": self._generate_approval_items(input_data)
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        reasoning = input_data.get("reasoning_decision_output", {})
        knowledge = input_data.get("knowledge_retrieval_output", {})
        trip_data = input_data.get("trip_data", {})

        approval_form = self._generate_approval_form(trip_data, reasoning, knowledge)

        html_content = self._generate_html(approval_form)
        pdf_bytes = self._generate_pdf(approval_form)

        response_data = {
            "status": "completed",
            "approval_form": approval_form,
            "total_cost": reasoning.get("total_cost", 0),
            "needs_special_approval": reasoning.get("needs_special_approval", False),
            "message": "审批单生成完成",
            "html": html_content,
            "pdf_size": len(pdf_bytes) if pdf_bytes else 0
        }

        reasoning_steps = [
            f"生成审批单",
            f"总费用: {response_data['total_cost']}元",
            f"需要特殊审批: {'是' if response_data['needs_special_approval'] else '否'}",
            f"HTML长度: {len(html_content)}字符",
            f"PDF大小: {len(pdf_bytes) if pdf_bytes else 0}字节"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    def _extract_cost(self, data: Any, category: str) -> float:
        if not data:
            return 0.0

        if isinstance(data, dict):
            if "price" in data:
                return float(data.get("price", 0))
            if "total_amount" in data:
                return float(data.get("total_amount", 0))
            if "options" in data and isinstance(data["options"], list):
                return sum(self._extract_cost(opt, category) for opt in data["options"])

        if isinstance(data, list):
            return sum(self._extract_cost(item, category) for item in data)

        return 0.0

    def _generate_approval_items(self, input_data: dict) -> List[dict]:
        items = []
        transport = input_data.get("transport_data", {})
        hotel = input_data.get("hotel_data", {})
        dining = input_data.get("dining_data", {})

        if transport:
            items.append({
                "category": "transport",
                "description": "出行费用",
                "amount": self._extract_cost(transport, "transport")
            })

        if hotel:
            items.append({
                "category": "hotel",
                "description": "住宿费用",
                "amount": self._extract_cost(hotel, "hotel")
            })

        if dining:
            items.append({
                "category": "dining",
                "description": "餐饮费用",
                "amount": self._extract_cost(dining, "dining")
            })

        return items

    def _generate_approval_form(
        self,
        trip_data: dict,
        reasoning: dict,
        knowledge: dict
    ) -> dict:
        return {
            "form_id": f"approval_{id(trip_data)}",
            "basic_info": {
                "employee_name": trip_data.get("employee_name", "未知"),
                "user_level": trip_data.get("user_level", "基层员工"),
                "department": trip_data.get("department", "未知"),
                "purpose": trip_data.get("purpose", "商务出差")
            },
            "trip_details": {
                "departure": trip_data.get("departure", "未知"),
                "destination": trip_data.get("destination", "未知"),
                "start_date": trip_data.get("start_date", "未知"),
                "end_date": trip_data.get("end_date", "未知")
            },
            "cost_summary": {
                "transport": reasoning.get("transport_cost", 0),
                "hotel": reasoning.get("hotel_cost", 0),
                "dining": reasoning.get("dining_cost", 0),
                "total": reasoning.get("total_cost", 0)
            },
            "approval_chain": knowledge.get("approval_chain", []),
            "items": reasoning.get("approval_items", []),
            "needs_special_approval": reasoning.get("needs_special_approval", False)
        }

    def _generate_html(self, approval_form: dict) -> str:
        from app.services.pdf_generator import pdf_generator
        return pdf_generator.generate_html(approval_form)

    def _generate_pdf(self, approval_form: dict) -> bytes:
        from app.services.pdf_generator import pdf_generator
        try:
            return pdf_generator.generate_approval_pdf(approval_form)
        except Exception as e:
            self.logger.error(f"PDF generation error: {e}")
            return b""

    async def _simple_generate(self, input_data: dict) -> dict:
        trip_data = input_data.get("trip_data", {})
        transport_data = input_data.get("transport", {})
        hotel_data = input_data.get("hotel", {})
        dining_data = input_data.get("dining", {})

        total_cost = (
            self._extract_cost(transport_data, "transport") +
            self._extract_cost(hotel_data, "hotel") +
            self._extract_cost(dining_data, "dining")
        )

        approval_form = self._generate_approval_form(
            trip_data,
            {"total_cost": total_cost, "transport_cost": self._extract_cost(transport_data, "transport"),
             "hotel_cost": self._extract_cost(hotel_data, "hotel"),
             "dining_cost": self._extract_cost(dining_data, "dining")},
            {}
        )

        html_content = self._generate_html(approval_form)
        pdf_bytes = self._generate_pdf(approval_form)

        return {
            "status": "completed",
            "total_cost": total_cost,
            "approval_form": approval_form,
            "html": html_content,
            "pdf_size": len(pdf_bytes) if pdf_bytes else 0,
            "message": "审批单生成完成"
        }

    async def generate_html(self, summary: dict) -> str:
        form = summary.get("approval_form", {})
        return self._generate_html(form)

    async def generate_pdf(self, summary: dict) -> bytes:
        form = summary.get("approval_form", {})
        return self._generate_pdf(form)

    async def create_approval_record(self, trip_id: str, pdf_url: str = None) -> dict:
        return {
            "status": "created",
            "trip_id": trip_id,
            "pdf_url": pdf_url,
            "message": "审批记录创建成功"
        }