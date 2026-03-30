from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from app.cot.knowledge_base import knowledge_base
from typing import List, Dict, Any
from app.utils.logger import logger
import json


MOCK_FLIGHTS = [
    {"id": "flight_001", "type": "flight", "provider": "中国国航", "flight_no": "CA1234",
     "departure_city": "北京", "departure_code": "PEK", "departure_time": "08:30",
     "arrival_city": "上海", "arrival_code": "PVG", "arrival_time": "10:45",
     "duration": "2小时15分钟", "price": 680.0},
    {"id": "flight_002", "type": "flight", "provider": "东方航空", "flight_no": "MU5678",
     "departure_city": "北京", "departure_code": "PEK", "departure_time": "14:20",
     "arrival_city": "上海", "arrival_code": "PVG", "arrival_time": "16:35",
     "duration": "2小时15分钟", "price": 720.0},
    {"id": "flight_003", "type": "flight", "provider": "南方航空", "flight_no": "CZ3089",
     "departure_city": "北京", "departure_code": "PEK", "departure_time": "10:00",
     "arrival_city": "广州", "arrival_code": "CAN", "arrival_time": "13:30",
     "duration": "3小时30分钟", "price": 1200.0},
]

MOCK_TRAINS = [
    {"id": "train_001", "type": "train", "provider": "高铁", "train_no": "G101",
     "departure_city": "北京", "departure_code": "BJN", "departure_time": "07:00",
     "arrival_city": "上海", "arrival_code": "SHH", "arrival_time": "12:30",
     "duration": "5小时30分钟", "price": 553.0},
    {"id": "train_002", "type": "train", "provider": "高铁", "train_no": "G201",
     "departure_city": "北京", "departure_code": "BJN", "departure_time": "09:00",
     "arrival_city": "上海", "arrival_code": "SHH", "arrival_time": "14:30",
     "duration": "5小时30分钟", "price": 553.0},
    {"id": "train_003", "type": "train", "provider": "高铁", "train_no": "G301",
     "departure_city": "北京", "departure_code": "BJN", "departure_time": "08:00",
     "arrival_city": "武汉", "arrival_code": "WHN", "arrival_time": "12:30",
     "duration": "4小时30分钟", "price": 520.0},
]


class TransportationAgent(BaseAgent):
    def __init__(self):
        super().__init__("TransportationAgent")

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)
        return await self._simple_search(input_data)

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"transport_{id(input_data)}",
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
            self.logger.error(f"TransportationAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_search(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        departure = input_data.get("departure")
        destination = input_data.get("destination")
        date = input_data.get("date")
        transport_type = input_data.get("type", "both")
        user_level = input_data.get("user_level", "基层员工")

        reasoning_steps = [
            f"解析出行需求：{departure} → {destination}",
            f"出行日期：{date}",
            f"偏好交通方式：{transport_type}",
            f"用户职级：{user_level}"
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "departure": departure,
                "destination": destination,
                "date": date,
                "transport_type": transport_type,
                "user_level": user_level,
                "search_scope": f"{departure}-{destination}"
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        user_level = input_data.get("user_level", "基层员工")
        destination = input_data.get("destination", "一线")
        transport_type = input_data.get("transport_type", "both")

        city_tier = knowledge_base.retrieve_city_tier(destination)
        flight_policy = knowledge_base.retrieve_policies("flight", user_level)
        train_policy = knowledge_base.retrieve_policies("train", user_level)

        reasoning_steps = [
            f"检索目的地城市等级：{city_tier}",
            f"检索{user_level}的航班规定：{flight_policy.get('description', 'N/A')}",
            f"检索{user_level}的高铁规定：{train_policy.get('seat', 'N/A')}",
            f"航班费用上限：{flight_policy.get('max_price', 'N/A')}元",
            f"舱位类型：{flight_policy.get('cabin', 'N/A')}"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "city_tier": city_tier,
                "flight_policy": flight_policy,
                "train_policy": train_policy,
                "flight_budget": flight_policy.get("max_price", 1000),
                "train_budget": train_policy.get("max_price", 1000),
                "allowed_cabin": flight_policy.get("cabin", "经济舱"),
                "transport_type": transport_type,
                "user_level": user_level,
                "departure": input_data.get("departure"),
                "destination": destination
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        flight_budget = input_data.get("flight_budget", 1000)
        train_budget = input_data.get("train_budget", 1000)
        transport_type = input_data.get("transport_type", "both")
        departure = input_data.get("departure", "")
        destination = input_data.get("destination", "")

        all_options = self._search_all_options({
            "departure": departure,
            "destination": destination
        })

        flight_options = [o for o in all_options if o["type"] == "flight"]
        train_options = [o for o in all_options if o["type"] == "train"]

        compliant_flights = [f for f in flight_options if f["price"] <= flight_budget]
        compliant_trains = [t for t in train_options if t["price"] <= train_budget]

        over_budget_flights = [f for f in flight_options if f["price"] > flight_budget]
        over_budget_trains = [t for t in train_options if t["price"] > train_budget]

        recommendations = self._generate_recommendations(
            compliant_flights, compliant_trains,
            over_budget_flights, over_budget_trains,
            transport_type, flight_budget
        )

        knowledge = input_data.get("knowledge_retrieval_output", input_data)
        flight_policy = knowledge.get("flight_policy", {})
        train_policy = knowledge.get("train_policy", {})

        reasoning_steps = [
            f"搜索到{len(flight_options)}个航班选项，{len(compliant_flights)}个符合差标",
            f"搜索到{len(train_options)}个高铁选项，{len(compliant_trains)}个符合差标",
            f"航班预算：{flight_budget}元，高铁预算：{train_budget}元",
            f"生成{len(recommendations)}条推荐方案"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "all_options": all_options,
                "compliant_flights": compliant_flights,
                "compliant_trains": compliant_trains,
                "over_budget_flights": over_budget_flights,
                "over_budget_trains": over_budget_trains,
                "recommendations": recommendations,
                "has_compliant_options": len(compliant_flights) > 0 or len(compliant_trains) > 0,
                "flight_budget": flight_budget,
                "train_budget": train_budget,
                "transport_type": transport_type,
                "flight_policy": flight_policy,
                "train_policy": train_policy
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        recommendations = input_data.get("recommendations", [])
        has_compliant = input_data.get("has_compliant_options", False)
        flight_policy = input_data.get("flight_policy", {})
        train_policy = input_data.get("train_policy", {})

        response_data = {
            "status": "completed",
            "has_compliant_options": has_compliant,
            "recommendations": recommendations,
            "total_options": len(recommendations),
            "flight_policy": flight_policy,
            "train_policy": train_policy
        }

        reasoning_steps = [
            f"生成出行方案响应",
            f"包含{len(recommendations)}个推荐方案",
            f"合规方案可用：{has_compliant}"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    def _search_all_options(self, input_data: dict) -> List[dict]:
        departure = input_data.get("departure", "")
        destination = input_data.get("destination", "")
        results = []

        for flight in MOCK_FLIGHTS:
            if (departure in flight["departure_city"] or departure in flight["departure_city"]) and \
               destination in flight["arrival_city"]:
                results.append({
                    "id": flight["id"],
                    "type": "flight",
                    "provider": flight["provider"],
                    "flight_no": flight["flight_no"],
                    "departure": {
                        "city": flight["departure_city"],
                        "code": flight["departure_code"],
                        "time": flight["departure_time"]
                    },
                    "arrival": {
                        "city": flight["arrival_city"],
                        "code": flight["arrival_code"],
                        "time": flight["arrival_time"]
                    },
                    "duration": flight["duration"],
                    "price": flight["price"]
                })

        for train in MOCK_TRAINS:
            if (departure in train["departure_city"] or departure in train["departure_city"]) and \
               destination in train["arrival_city"]:
                results.append({
                    "id": train["id"],
                    "type": "train",
                    "provider": train["provider"],
                    "train_no": train["train_no"],
                    "departure": {
                        "city": train["departure_city"],
                        "code": train["departure_code"],
                        "time": train["departure_time"]
                    },
                    "arrival": {
                        "city": train["arrival_city"],
                        "code": train["arrival_code"],
                        "time": train["arrival_time"]
                    },
                    "duration": train["duration"],
                    "price": train["price"]
                })

        return results

    def _generate_recommendations(
        self,
        compliant_flights: List[dict],
        compliant_trains: List[dict],
        over_budget_flights: List[dict],
        over_budget_trains: List[dict],
        transport_type: str,
        flight_budget: float,
        train_budget: float = 1000
    ) -> List[dict]:
        recommendations = []

        if transport_type in ["train"]:
            if compliant_trains:
                best_train = min(compliant_trains, key=lambda x: x["price"])
                recommendations.append({
                    "category": "recommended",
                    "type": "train",
                    "option": best_train,
                    "compliance": {
                        "is_compliant": True,
                        "limit": train_budget,
                        "savings": train_budget - best_train["price"]
                    },
                    "reason": "高铁出行，符合差旅标准"
                })
                
                if over_budget_trains:
                    cheapest_expensive_train = min(over_budget_trains, key=lambda x: x["price"])
                    recommendations.append({
                        "category": "alternative",
                        "type": "train",
                        "option": cheapest_expensive_train,
                        "compliance": {
                            "is_compliant": False,
                            "limit": train_budget,
                            "over_budget": cheapest_expensive_train["price"] - train_budget
                        },
                        "reason": f"超标{cheapest_expensive_train['price'] - train_budget}元，但您仍可选择"
                    })
                
                if compliant_flights:
                    best_flight = min(compliant_flights, key=lambda x: x["price"])
                    recommendations.append({
                        "category": "sync_recommend",
                        "type": "flight",
                        "option": best_flight,
                        "compliance": {
                            "is_compliant": True,
                            "limit": flight_budget,
                            "savings": flight_budget - best_flight["price"]
                        },
                        "reason": f"特价机票{best_flight['price']}元，比高铁更便宜"
                    })
                        
            elif over_budget_trains:
                cheapest_expensive_train = min(over_budget_trains, key=lambda x: x["price"])
                recommendations.append({
                    "category": "alternative",
                    "type": "train",
                    "option": cheapest_expensive_train,
                    "compliance": {
                        "is_compliant": False,
                        "limit": train_budget,
                        "over_budget": cheapest_expensive_train["price"] - train_budget
                    },
                    "reason": f"超标{cheapest_expensive_train['price'] - train_budget}元，建议选择更经济的方案"
                })
                
                if compliant_flights:
                    best_flight = min(compliant_flights, key=lambda x: x["price"])
                    recommendations.append({
                        "category": "sync_recommend",
                        "type": "flight",
                        "option": best_flight,
                        "compliance": {
                            "is_compliant": True,
                            "limit": flight_budget,
                            "savings": flight_budget - best_flight["price"]
                        },
                        "reason": f"特价机票{best_flight['price']}元，符合差旅标准且更便宜"
                    })
                elif over_budget_flights:
                    cheapest_flight = min(over_budget_flights, key=lambda x: x["price"])
                    recommendations.append({
                        "category": "sync_recommend",
                        "type": "flight",
                        "option": cheapest_flight,
                        "compliance": {
                            "is_compliant": False,
                            "limit": flight_budget,
                            "over_budget": cheapest_flight["price"] - flight_budget
                        },
                        "reason": f"机票{cheapest_flight['price']}元，是当前可选的最优方案"
                    })

        elif transport_type in ["flight", "both"]:
            if compliant_flights:
                best_flight = min(compliant_flights, key=lambda x: x["price"])
                recommendations.append({
                    "category": "recommended",
                    "type": "flight",
                    "option": best_flight,
                    "compliance": {
                        "is_compliant": True,
                        "limit": flight_budget,
                        "savings": flight_budget - best_flight["price"]
                    },
                    "reason": "符合差旅标准的价格最优航班"
                })

            if over_budget_flights and transport_type == "both":
                cheapest_over = min(over_budget_flights, key=lambda x: x["price"])
                recommendations.append({
                    "category": "alternative",
                    "type": "flight",
                    "option": cheapest_over,
                    "compliance": {
                        "is_compliant": False,
                        "limit": flight_budget,
                        "over_budget": cheapest_over["price"] - flight_budget
                    },
                    "reason": f"超出差标{cheapest_over['price'] - flight_budget}元"
                })

        if transport_type in ["train", "both"]:
            if compliant_trains and transport_type == "both":
                best_train = min(compliant_trains, key=lambda x: x["price"])
                recommendations.append({
                    "category": "recommended",
                    "type": "train",
                    "option": best_train,
                    "compliance": {
                        "is_compliant": True,
                        "limit": train_budget,
                        "savings": train_budget - best_train["price"]
                    },
                    "reason": "高铁出行，符合差旅标准"
                })

            if over_budget_trains and transport_type == "both":
                cheapest_over = min(over_budget_trains, key=lambda x: x["price"])
                recommendations.append({
                    "category": "alternative",
                    "type": "train",
                    "option": cheapest_over,
                    "compliance": {
                        "is_compliant": False,
                        "limit": train_budget,
                        "over_budget": cheapest_over["price"] - train_budget
                    },
                    "reason": f"超出差标{cheapest_over['price'] - train_budget}元"
                })

        return recommendations

    async def _simple_search(self, input_data: dict) -> dict:
        departure = input_data.get("departure")
        destination = input_data.get("destination")
        date = input_data.get("date")
        transport_type = input_data.get("type", "both")

        results = self._search_all_options({
            "departure": departure,
            "destination": destination,
            "date": date,
            "type": transport_type
        })

        return {
            "status": "completed",
            "options": results,
            "count": len(results)
        }

    async def book_transport(self, input_data: dict) -> dict:
        option_id = input_data.get("option_id")
        booking_id = f"booking_{option_id}_{hash(option_id) % 10000}"

        return {
            "status": "confirmed",
            "booking_id": booking_id,
            "message": "预订成功（Mock）"
        }