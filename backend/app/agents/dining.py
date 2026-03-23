from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from app.cot.knowledge_base import knowledge_base
from typing import List, Dict, Any
from app.utils.logger import logger


MOCK_RESTAURANTS = [
    {"id": "restaurant_001", "restaurant": "上海老饭店", "cuisine": "本帮菜", "city": "上海",
     "address": "上海市黄浦区福佑路168号", "price_per_person": 200.0, "has_private_room": True,
     "recommended_dishes": [
         {"name": "蟹粉小笼", "price": 88.0, "suitable_for": 3},
         {"name": "红烧肉", "price": 68.0, "suitable_for": 4},
         {"name": "清炒虾仁", "price": 98.0, "suitable_for": 4}
     ]},
    {"id": "restaurant_002", "restaurant": "绿波廊", "cuisine": "本帮菜", "city": "上海",
     "address": "上海市黄浦区豫园路125号", "price_per_person": 180.0, "has_private_room": True,
     "recommended_dishes": [
         {"name": "蟹粉豆腐", "price": 78.0, "suitable_for": 3},
         {"name": "八宝辣酱", "price": 58.0, "suitable_for": 4}
     ]},
    {"id": "restaurant_003", "restaurant": "新荣记", "cuisine": "台州菜", "city": "上海",
     "address": "上海市静安区南京西路1266号", "price_per_person": 280.0, "has_private_room": True,
     "recommended_dishes": [
         {"name": "野生大黄鱼", "price": 388.0, "suitable_for": 5},
         {"name": "沙蒜豆面", "price": 128.0, "suitable_for": 4}
     ]},
    {"id": "restaurant_004", "restaurant": "鼎泰丰", "cuisine": "淮扬菜", "city": "上海",
     "address": "上海市黄浦区南京东路719号", "price_per_person": 150.0, "has_private_room": False,
     "recommended_dishes": [
         {"name": "小笼包", "price": 68.0, "suitable_for": 4},
         {"name": "红烧牛肉面", "price": 88.0, "suitable_for": 1}
     ]},
    {"id": "restaurant_005", "restaurant": "广州酒家", "cuisine": "粤菜", "city": "北京",
     "address": "北京市朝阳区东三环中路9号", "price_per_person": 220.0, "has_private_room": True,
     "recommended_dishes": [
         {"name": "白切鸡", "price": 128.0, "suitable_for": 4},
         {"name": "虾饺皇", "price": 78.0, "suitable_for": 3}
     ]},
    {"id": "restaurant_006", "restaurant": "全聚德", "cuisine": "京菜", "city": "北京",
     "address": "北京市东城区前门大街30号", "price_per_person": 260.0, "has_private_room": True,
     "recommended_dishes": [
         {"name": "北京烤鸭", "price": 288.0, "suitable_for": 5},
         {"name": "炸酱面", "price": 48.0, "suitable_for": 1}
     ]},
]


class DiningAgent(BaseAgent):
    def __init__(self):
        super().__init__("DiningAgent")

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)
        return await self._simple_search(input_data)

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"dining_{id(input_data)}",
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
            self.logger.error(f"DiningAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_search(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        city = input_data.get("city")
        date = input_data.get("date")
        headcount = input_data.get("headcount", 1)
        cuisine = input_data.get("cuisine")
        budget_per_person = input_data.get("budget_per_person")

        reasoning_steps = [
            f"解析宴请需求：{city}",
            f"宴请日期：{date or '未指定'}",
            f"用餐人数：{headcount}人",
            f"偏好菜系：{cuisine or '不限'}",
            f"预算人均：{budget_per_person or '未指定'}元"
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "city": city,
                "date": date,
                "headcount": headcount,
                "cuisine": cuisine,
                "budget_per_person": budget_per_person
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        city = input_data.get("city", "一线")

        city_tier = knowledge_base.retrieve_city_tier(city)
        dining_policy = knowledge_base.retrieve_policies("dining", None)

        if isinstance(dining_policy, dict):
            dining_limit = dining_policy.get(city_tier, 200)
        else:
            dining_limit = 200

        reasoning_steps = [
            f"检索城市等级：{city} -> {city_tier}",
            f"检索{city_tier}城市公务接待宴请标准：人均{dining_limit}元",
            f"检索差旅餐饮补贴政策..."
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "city_tier": city_tier,
                "dining_limit": dining_limit,
                "dining_policy": dining_policy
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        knowledge = input_data.get("knowledge_retrieval_output", {})
        dining_limit = knowledge.get("dining_limit", 200)
        city = input_data.get("city")
        cuisine = input_data.get("cuisine")
        headcount = input_data.get("headcount", 1)
        budget_per_person = input_data.get("budget_per_person")

        all_restaurants = self._search_restaurants_in_city(city, cuisine)

        user_budget = budget_per_person or dining_limit
        is_over_budget = budget_per_person and budget_per_person > dining_limit

        compliant_restaurants = []
        over_budget_restaurants = []

        for restaurant in all_restaurants:
            price = restaurant["price_per_person"]
            total_amount = price * headcount

            if price <= dining_limit:
                compliant_restaurants.append({
                    **restaurant,
                    "total_amount": total_amount,
                    "compliance": {
                        "is_compliant": True,
                        "limit": dining_limit,
                        "over_budget": None
                    }
                })
            else:
                over_budget_restaurants.append({
                    **restaurant,
                    "total_amount": total_amount,
                    "compliance": {
                        "is_compliant": False,
                        "limit": dining_limit,
                        "over_budget": (price - dining_limit) * headcount
                    }
                })

        compliant_restaurants.sort(key=lambda x: x["price_per_person"])
        over_budget_restaurants.sort(key=lambda x: x["price_per_person"])

        compliant_recommendations = self._generate_recommendations(compliant_restaurants[:3], headcount, True, dining_limit)
        over_budget_recommendations = self._generate_recommendations(over_budget_restaurants[:3], headcount, False, user_budget)

        reasoning_steps = [
            f"搜索到{len(all_restaurants)}家餐厅",
            f"宴请标准（{dining_limit}元/人）：符合{len(compliant_restaurants)}家，超标{len(over_budget_restaurants)}家",
            f"用户预算：{user_budget}元/人 {'（超标）' if is_over_budget else ''}",
            f"生成合规推荐{len(compliant_recommendations)}家，替代推荐{len(over_budget_recommendations)}家"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "all_restaurants": all_restaurants,
                "compliant_restaurants": compliant_restaurants,
                "over_budget_restaurants": over_budget_restaurants,
                "compliant_recommendations": compliant_recommendations,
                "over_budget_recommendations": over_budget_recommendations,
                "dining_limit": dining_limit,
                "user_budget": user_budget,
                "is_over_budget": is_over_budget,
                "has_compliant_options": len(compliant_restaurants) > 0
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        reasoning = input_data.get("reasoning_decision_output", {})
        knowledge = input_data.get("knowledge_retrieval_output", {})
        city_tier = knowledge.get("city_tier", "一线")
        dining_limit = reasoning.get("dining_limit", 200)

        response_data = {
            "status": "completed",
            "is_over_budget": reasoning.get("is_over_budget", False),
            "compliant_restaurants": reasoning.get("compliant_recommendations", []),
            "over_budget_restaurants": reasoning.get("over_budget_recommendations", []),
            "total_compliant": len(reasoning.get("compliant_restaurants", [])),
            "total_over_budget": len(reasoning.get("over_budget_restaurants", [])),
            "dining_limit": dining_limit,
            "city_tier": city_tier
        }

        reasoning_steps = [
            f"生成宴请推荐响应",
            f"合规推荐：{len(response_data['compliant_restaurants'])}家",
            f"超标推荐：{len(response_data['over_budget_restaurants'])}家",
            f"宴请标准：{dining_limit}元/人（{city_tier}城市）"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    def _search_restaurants_in_city(self, city: str, cuisine: str = None) -> List[dict]:
        results = []
        for r in MOCK_RESTAURANTS:
            if r["city"] != city:
                continue
            if cuisine and r["cuisine"] != cuisine:
                continue
            results.append({
                "id": r["id"],
                "restaurant": r["restaurant"],
                "cuisine": r["cuisine"],
                "city": r["city"],
                "address": r["address"],
                "price_per_person": r["price_per_person"],
                "has_private_room": r["has_private_room"],
                "recommended_dishes": r["recommended_dishes"]
            })
        return results

    def _generate_recommendations(
        self,
        restaurants: List[dict],
        headcount: int,
        is_compliant: bool,
        budget: float = None
    ) -> List[dict]:
        recommendations = []
        for restaurant in restaurants:
            dish_result = self._suggest_dishes(restaurant["recommended_dishes"], headcount, budget)
            dishes = dish_result.get("dishes", []) if isinstance(dish_result, dict) else dish_result
            total_dishes_price = dish_result.get("total_price", 0) if isinstance(dish_result, dict) else sum(d["price"] for d in dishes)

            recommendations.append({
                "id": restaurant["id"],
                "restaurant": restaurant["restaurant"],
                "cuisine": restaurant["cuisine"],
                "city": restaurant["city"],
                "address": restaurant["address"],
                "price_per_person": restaurant["price_per_person"],
                "headcount": headcount,
                "total_amount": restaurant["price_per_person"] * headcount,
                "has_private_room": restaurant["has_private_room"],
                "suggested_dishes": dishes,
                "dishes_total_price": total_dishes_price,
                "compliance": restaurant["compliance"]
            })
        return recommendations

    def _suggest_dishes(self, dishes: List[dict], headcount: int, budget: float = None) -> List[dict]:
        if not dishes:
            return []

        sorted_dishes = sorted(dishes, key=lambda x: x.get("suitable_for", 1), reverse=True)
        suggested = []
        remaining = headcount
        total_price = 0.0

        for dish in sorted_dishes:
            dish_price = dish.get("price", 0)
            dish_suitable = dish.get("suitable_for", 1)
            
            if budget and (total_price + dish_price) > budget:
                continue
            
            if remaining >= dish_suitable:
                suggested.append(dish)
                total_price += dish_price
                remaining -= dish_suitable

        if not suggested and dishes:
            budget_dishes = [d for d in dishes if not budget or d.get("price", 0) <= budget]
            if budget_dishes:
                first = budget_dishes[0]
                suggested.append(first)
                total_price = first.get("price", 0)

        return {
            "dishes": suggested,
            "total_price": total_price,
            "coverage": headcount - remaining
        }

    async def _simple_search(self, input_data: dict) -> dict:
        city = input_data.get("city")
        date = input_data.get("date")
        headcount = input_data.get("headcount", 1)
        cuisine = input_data.get("cuisine")
        budget_per_person = input_data.get("budget_per_person")

        city_tier = knowledge_base.retrieve_city_tier(city)
        dining_policy = knowledge_base.retrieve_policies("dining", None)

        if isinstance(dining_policy, dict):
            dining_limit = dining_policy.get(city_tier, 200)
        else:
            dining_limit = 200

        all_restaurants = self._search_restaurants_in_city(city, cuisine)

        compliant_restaurants = []
        over_budget_restaurants = []

        for restaurant in all_restaurants:
            total_amount = restaurant["price_per_person"] * headcount
            is_compliant = restaurant["price_per_person"] <= dining_limit
            restaurant["is_compliant"] = is_compliant
            restaurant["compliance"] = {
                "is_compliant": is_compliant,
                "limit": dining_limit,
                "over_budget": (restaurant["price_per_person"] - dining_limit) * headcount if not is_compliant else None
            }

            restaurant_data = self._generate_recommendations([restaurant], headcount, is_compliant, dining_limit)
            if is_compliant:
                compliant_restaurants.extend(restaurant_data)
            else:
                over_budget_restaurants.extend(restaurant_data)

        return {
            "status": "completed",
            "compliant_restaurants": compliant_restaurants,
            "over_budget_restaurants": over_budget_restaurants,
            "total_compliant": len(compliant_restaurants),
            "total_over_budget": len(over_budget_restaurants)
        }

    async def reserve_dining(self, input_data: dict) -> dict:
        option_id = input_data.get("option_id")
        booking_id = f"dining_booking_{option_id}_{hash(option_id) % 10000}"

        return {
            "status": "confirmed",
            "booking_id": booking_id,
            "message": "餐厅预约成功（Mock）"
        }