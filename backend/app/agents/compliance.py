from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from app.cot.knowledge_base import knowledge_base
from typing import Dict, List, Any
from app.utils.logger import logger


class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ComplianceAgent")
        self.rules = self._init_rules()

    def _init_rules(self) -> dict:
        return {
            "hotel": {
                "基层员工": {"一线": 400, "新一线": 350, "二线": 300, "其他": 260},
                "主管/资深专员": {"一线": 500, "新一线": 450, "二线": 400, "其他": 350},
                "经理级": {"一线": 650, "新一线": 600, "二线": 550, "其他": 500},
                "总监级": {"一线": 800, "新一线": 750, "二线": 700, "其他": 650},
                "副总/高管": {"一线": 1200, "新一线": 1000, "二线": 900, "其他": 800}
            },
            "dining": {
                "一线": 300,
                "新一线": 260,
                "其他": 200
            },
            "transport": {
                "flight": {
                    "基层员工": {"max_price": 1000, "cabin": "经济舱折扣票"},
                    "主管/资深专员": {"max_price": 1500, "cabin": "经济舱"},
                    "经理级": {"max_price": 2000, "cabin": "经济舱/高端经济舱"},
                    "总监级": {"max_price": 3000, "cabin": "商务舱折扣票"},
                    "副总/高管": {"max_price": 5000, "cabin": "商务舱/头等舱"}
                },
                "train": {
                    "基层员工": {"seat": "二等座"},
                    "主管/资深专员": {"seat": "二等座（一等座需申请）"},
                    "经理级": {"seat": "一等座"},
                    "总监级": {"seat": "一等座/商务座"},
                    "副总/高管": {"seat": "一等座/商务座"}
                }
            }
        }

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)

        action = input_data.get("action", "check")
        if action == "check":
            return await self._simple_check(input_data)
        elif action == "check_user_level":
            return await self._simple_check_user_level(input_data)
        return {"status": "error", "message": f"Unknown action: {action}"}

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"compliance_{id(input_data)}",
            agent_name=self.name
        )

        try:
            layer1 = await self.intent_understanding_layer(input_data, cot_result)
            cot_result.layers.append(layer1)

            layer2_input = {**layer1.output_data, "original_input": input_data}
            layer2 = await self.knowledge_retrieval_layer(layer2_input, cot_result)
            cot_result.layers.append(layer2)

            layer3_input = {**layer2.output_data, "original_input": input_data}
            layer3 = await self.reasoning_decision_layer(layer3_input, cot_result)
            cot_result.layers.append(layer3)

            layer4_input = {**layer3.output_data, "original_input": input_data}
            layer4 = await self.response_generation_layer(layer4_input, cot_result)
            cot_result.layers.append(layer4)

            cot_result.final_output = layer4.output_data
            cot_result.is_complete = True

            return {
                **layer4.output_data,
                "cot": cot_result.to_dict()
            }
        except Exception as e:
            self.logger.error(f"ComplianceAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_check(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        category = input_data.get("category")
        amount = input_data.get("amount")
        user_level = input_data.get("user_level", "基层员工")
        city = input_data.get("city", "一线")
        transport_type = input_data.get("transport_type", "flight")

        reasoning_steps = [
            f"解析合规检查请求",
            f"费用类别：{category}",
            f"金额：{amount}元",
            f"用户职级：{user_level}",
            f"目的地城市：{city}"
        ]

        if category == "transport":
            reasoning_steps.append(f"交通类型：{transport_type}")

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "category": category,
                "amount": amount,
                "user_level": user_level,
                "city": city,
                "transport_type": transport_type
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        category = input_data.get("category")
        user_level = input_data.get("user_level", "基层员工")
        city = input_data.get("city", "一线")
        transport_type = input_data.get("transport_type", "flight")

        city_tier = knowledge_base.retrieve_city_tier(city)

        if category == "hotel":
            rules = self.rules["hotel"].get(user_level, {})
            limit = rules.get(city_tier, 400)
            rule_desc = f"{user_level}在{city_tier}城市住宿标准：{limit}元/晚"
        elif category == "dining":
            limit = self.rules["dining"].get(city_tier, 200)
            rule_desc = f"{city_tier}城市公务接待宴请标准：{limit}元/人"
        elif category == "transport":
            rules = self.rules["transport"].get(transport_type, {}).get(user_level, {})
            limit = rules.get("max_price", 1000)
            cabin = rules.get("cabin", "经济舱")
            rule_desc = f"{user_level}{transport_type}标准：{limit}元，{cabin}"
        else:
            limit = 0
            rule_desc = "未知类别"

        reasoning_steps = [
            f"检索城市等级：{city} -> {city_tier}",
            f"检索差旅标准规则：{rule_desc}",
            f"合规判断阈值：{limit}元"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "city_tier": city_tier,
                "limit": limit,
                "rule_desc": rule_desc,
                "category": category,
                "user_level": user_level
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        original_input = input_data.get("original_input", {})
        amount = original_input.get("amount") or input_data.get("amount")
        limit = input_data.get("limit", 0)
        category = input_data.get("category")

        is_compliant = amount <= limit
        over_budget = amount - limit if not is_compliant else 0
        compliance_rate = min(amount / limit, 1.5) if limit > 0 else 1.0

        if is_compliant:
            risk_level = "low"
            suggestion = "符合差旅标准"
        elif limit > 0 and over_budget / limit <= 0.2:
            risk_level = "medium"
            suggestion = f"轻微超标，建议选择更经济的方案"
        else:
            risk_level = "high"
            suggestion = f"严重超标，建议选择低价方案或申请特殊审批"

        reasoning_steps = [
            f"合规判定：{'通过' if is_compliant else '未通过'}",
            f"实际费用：{amount}元，标准上限：{limit}元",
            f"超标金额：{over_budget}元（{over_budget/limit*100:.1f}%）" if not is_compliant and limit > 0 else f"低于标准：{limit - amount}元" if is_compliant else f"超标金额：{over_budget}元",
            f"风险等级：{risk_level}",
            f"建议：{suggestion}"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "is_compliant": is_compliant,
                "limit": limit,
                "actual": amount,
                "over_budget": over_budget,
                "compliance_rate": compliance_rate,
                "risk_level": risk_level,
                "suggestion": suggestion
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        knowledge = input_data.get("knowledge_retrieval_output", {})

        category = knowledge.get("category", "unknown")
        limit = input_data.get("limit", 0)
        actual = input_data.get("actual", 0)
        is_compliant = input_data.get("is_compliant", True)
        over_budget = input_data.get("over_budget", 0)
        risk_level = input_data.get("risk_level", "low")
        suggestion = input_data.get("suggestion", "")

        if category == "hotel":
            category_name = "住宿"
        elif category == "dining":
            category_name = "餐饮"
        elif category == "transport":
            category_name = "交通"
        else:
            category_name = category

        if is_compliant:
            message = f"✅ {category_name}费用合规。实际{actual}元，标准上限{limit}元。"
        else:
            message = f"⚠️ {category_name}费用超标。实际{actual}元，超标{over_budget}元（标准上限{limit}元）。{suggestion}"

        response_data = {
            "status": "completed",
            "category": category,
            "is_compliant": is_compliant,
            "limit": limit,
            "actual": actual,
            "over_budget": over_budget,
            "risk_level": risk_level,
            "suggestion": suggestion,
            "message": message
        }

        reasoning_steps = [
            f"生成合规检查报告",
            f"合规状态：{'通过' if is_compliant else '未通过'}",
            f"风险等级：{risk_level}",
            f"建议措施：{suggestion}"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def _simple_check(self, input_data: dict) -> dict:
        category = input_data.get("category")
        amount = input_data.get("amount")
        user_level = input_data.get("user_level", "基层员工")
        city = input_data.get("city", "一线")
        transport_type = input_data.get("transport_type", "flight")

        city_tier = knowledge_base.retrieve_city_tier(city)

        if category == "hotel":
            limit = self.rules["hotel"].get(user_level, {}).get(city_tier, 400)
        elif category == "dining":
            limit = self.rules["dining"].get(city_tier, 200)
        elif category == "transport":
            rules = self.rules["transport"].get(transport_type, {}).get(user_level, {})
            limit = rules.get("max_price", 1000)
        else:
            return {"is_compliant": True, "reason": "未知类别"}

        is_compliant = amount <= limit
        over_budget = amount - limit if not is_compliant else 0

        return {
            "category": category,
            "is_compliant": is_compliant,
            "limit": limit,
            "actual": amount,
            "over_budget": over_budget,
            "reason": f"{category}费用{'未超标' if is_compliant else f'超标{over_budget}元'}"
        }

    async def _simple_check_user_level(self, input_data: dict) -> dict:
        user_level = input_data.get("user_level", "基层员工")
        valid_levels = list(self.rules["hotel"].keys())
        is_valid = user_level in valid_levels

        return {
            "user_level": user_level,
            "is_valid": is_valid,
            "valid_levels": valid_levels,
            "message": f"职级{'有效' if is_valid else f'无效，有效值为: {valid_levels}'}"
        }

    async def check_compliance(self, input_data: dict) -> dict:
        return await self.process(input_data)

    async def check_hotel_compliance(self, user_level: str, city: str, amount: float) -> dict:
        return await self._simple_check({
            "category": "hotel",
            "user_level": user_level,
            "city": city,
            "amount": amount
        })

    async def check_transport_compliance(self, user_level: str, amount: float, transport_type: str = "flight") -> dict:
        return await self._simple_check({
            "category": "transport",
            "user_level": user_level,
            "amount": amount,
            "transport_type": transport_type
        })

    async def check_dining_compliance(self, city: str, amount: float) -> dict:
        return await self._simple_check({
            "category": "dining",
            "city": city,
            "amount": amount
        })

    async def generate_report(self, checks: List[dict]) -> dict:
        total_items = len(checks)
        compliant_items = sum(1 for c in checks if c.get("is_compliant", True))
        over_budget_items = total_items - compliant_items
        total_amount = sum(c.get("actual", 0) for c in checks)
        total_over_budget = sum(c.get("over_budget", 0) for c in checks)

        return {
            "status": "completed",
            "total_items": total_items,
            "compliant_items": compliant_items,
            "over_budget_items": over_budget_items,
            "total_amount": total_amount,
            "total_over_budget": total_over_budget,
            "compliance_rate": compliant_items / total_items if total_items > 0 else 1.0,
            "checks": checks
        }

    def get_city_tier(self, city: str) -> str:
        return knowledge_base.retrieve_city_tier(city)