from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from app.cot.knowledge_base import knowledge_base
from typing import List, Dict, Any, Optional
from app.utils.logger import logger
from app.services.amap import amap_service


MOCK_HOTELS = [
    {"id": "hotel_001", "name": "上海外滩中心酒店", "stars": 5, "city": "上海",
     "district": "黄浦区", "address": "上海市黄浦区中山东一路100号", "location": "121.4901,31.2405",
     "price": 1200.0, "distance_km": 0.5, "facilities": ["免费WiFi", "健身房", "游泳池", "餐厅", "会议室"]},
    {"id": "hotel_002", "name": "上海静安香格里拉大酒店", "stars": 5, "city": "上海",
     "district": "静安区", "address": "上海市静安区延安中路1218号", "location": "121.4512,31.2234",
     "price": 1100.0, "distance_km": 1.2, "facilities": ["免费WiFi", "健身房", "SPA", "餐厅"]},
    {"id": "hotel_003", "name": "上海金茂君悦大酒店", "stars": 5, "city": "上海",
     "district": "浦东新区", "address": "上海市浦东新区世纪大道88号", "location": "121.5042,31.2401",
     "price": 1050.0, "distance_km": 2.0, "facilities": ["免费WiFi", "健身房", "游泳池", "餐厅"]},
    {"id": "hotel_004", "name": "上海豫园万丽酒店", "stars": 4, "city": "上海",
     "district": "黄浦区", "address": "上海市黄浦区河南南路158号", "location": "121.4856,31.2289",
     "price": 650.0, "distance_km": 1.5, "facilities": ["免费WiFi", "健身房", "餐厅"]},
    {"id": "hotel_005", "name": "上海锦江之星", "stars": 3, "city": "上海",
     "district": "静安区", "address": "上海市静安区长安路500号", "location": "121.4632,31.2512",
     "price": 280.0, "distance_km": 2.5, "facilities": ["免费WiFi", "餐厅"]},
    {"id": "hotel_006", "name": "北京王府井希尔顿酒店", "stars": 5, "city": "北京",
     "district": "东城区", "address": "北京市东城区王府井大街8号", "location": "116.4094,39.9139",
     "price": 1100.0, "distance_km": 0.8, "facilities": ["免费WiFi", "健身房", "游泳池", "餐厅", "会议室"]},
    {"id": "hotel_007", "name": "北京金融街威斯汀酒店", "stars": 5, "city": "北京",
     "district": "西城区", "address": "北京市西城区金融街丙8号", "location": "116.3556,39.9122",
     "price": 1000.0, "distance_km": 1.0, "facilities": ["免费WiFi", "健身房", "SPA", "餐厅"]},
    {"id": "hotel_008", "name": "如家快捷酒店", "stars": 3, "city": "北京",
     "district": "朝阳区", "address": "北京市朝阳区东三环南路48号", "location": "116.4612,39.9534",
     "price": 300.0, "distance_km": 3.0, "facilities": ["免费WiFi"]},
]


class HotelAgent(BaseAgent):
    def __init__(self):
        super().__init__("HotelAgent")

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)
        return await self._simple_search(input_data)

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"hotel_{id(input_data)}",
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
            self.logger.error(f"HotelAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_search(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        city = input_data.get("city")
        check_in = input_data.get("check_in")
        check_out = input_data.get("check_out")
        star = input_data.get("star")
        user_level = input_data.get("user_level", "基层员工")
        customer_location = input_data.get("customer_location", "")

        reasoning_steps = [
            f"解析住宿需求：{city}",
            f"入住日期：{check_in}，退房日期：{check_out}",
            f"用户职级：{user_level}",
            f"期望酒店星级：{star or '不限'}",
            f"客户位置：{customer_location or '未指定'}"
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "star": star,
                "user_level": user_level,
                "customer_location": customer_location
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        city = input_data.get("city", "一线")
        user_level = input_data.get("user_level", "基层员工")

        city_tier = knowledge_base.retrieve_city_tier(city)
        hotel_policy = knowledge_base.retrieve_policies("hotel", user_level)

        budget_limit = hotel_policy.get(city_tier, 400) if isinstance(hotel_policy, dict) else 400

        reasoning_steps = [
            f"检索城市等级：{city} -> {city_tier}",
            f"检索{user_level}在{city_tier}城市的住宿标准：{budget_limit}元/晚",
            f"检索差旅政策中关于酒店的规定..."
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "city_tier": city_tier,
                "hotel_policy": hotel_policy,
                "budget_limit": budget_limit,
                "user_level": user_level
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        knowledge = input_data.get("knowledge_retrieval_output", {})
        budget_limit = knowledge.get("budget_limit", 400)
        city = input_data.get("city")
        customer_location = input_data.get("customer_location", "")
        use_amap = input_data.get("use_amap", True)

        all_hotels = self._search_hotels_in_city(city)

        if use_amap and customer_location:
            all_hotels = await self._calculate_real_distances(all_hotels, customer_location)

        compliant_hotels = [h for h in all_hotels if h["price"] <= budget_limit]
        alternative_hotels = [h for h in all_hotels if h["price"] > budget_limit]

        compliant_hotels.sort(key=lambda x: (x.get("real_distance_km", x.get("distance_km", 999)), -x["stars"]))
        alternative_hotels.sort(key=lambda x: (x.get("real_distance_km", x.get("distance_km", 999)), x["price"]))

        compliant_recommendations = self._generate_hotel_recommendations(compliant_hotels[:3], budget_limit, True)
        alternative_recommendations = self._generate_hotel_recommendations(alternative_hotels[:3], budget_limit, False)

        reasoning_steps = [
            f"搜索到{len(all_hotels)}家酒店",
            f"符合差标（≤{budget_limit}元）：{len(compliant_hotels)}家",
            f"超出差标：{len(alternative_hotels)}家",
            f"使用高德API计算真实距离：{'是' if use_amap and customer_location else '否'}",
            f"生成合规推荐{len(compliant_recommendations)}家，替代推荐{len(alternative_recommendations)}家"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "all_hotels": all_hotels,
                "compliant_hotels": compliant_hotels,
                "alternative_hotels": alternative_hotels,
                "compliant_recommendations": compliant_recommendations,
                "alternative_recommendations": alternative_recommendations,
                "budget_limit": budget_limit,
                "has_compliant_options": len(compliant_hotels) > 0,
                "used_real_distance": use_amap and customer_location
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        reasoning = input_data.get("reasoning_decision_output", {})
        knowledge = input_data.get("knowledge_retrieval_output", {})

        response_data = {
            "status": "completed",
            "compliant_hotels": reasoning.get("compliant_recommendations", []),
            "alternative_hotels": reasoning.get("alternative_recommendations", []),
            "total_compliant": len(reasoning.get("compliant_hotels", [])),
            "total_alternative": len(reasoning.get("alternative_hotels", [])),
            "budget_limit": reasoning.get("budget_limit", 400),
            "city_tier": knowledge.get("city_tier", "一线"),
            "used_real_distance": reasoning.get("used_real_distance", False)
        }

        reasoning_steps = [
            f"生成酒店推荐响应",
            f"合规推荐：{len(response_data['compliant_hotels'])}家",
            f"替代推荐：{len(response_data['alternative_hotels'])}家",
            f"预算上限：{response_data['budget_limit']}元/晚",
            f"使用真实距离计算：{'是' if response_data['used_real_distance'] else '否'}"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def _calculate_real_distances(self, hotels: List[dict], customer_location: str) -> List[dict]:
        customer_coords = await self._get_coordinates(customer_location)
        if not customer_coords:
            self.logger.warning(f"Could not geocode customer location: {customer_location}")
            return hotels

        updated_hotels = []
        for hotel in hotels:
            hotel_location = hotel.get("location")
            if hotel_location:
                distance = await amap_service.get_distance(customer_coords, hotel_location, "walking")
                if distance:
                    hotel["real_distance_km"] = distance / 1000.0
                    hotel["distance_source"] = "amap"
                else:
                    hotel["real_distance_km"] = hotel.get("distance_km", 1.0)
                    hotel["distance_source"] = "mock"
            else:
                hotel["real_distance_km"] = hotel.get("distance_km", 1.0)
                hotel["distance_source"] = "mock"
            updated_hotels.append(hotel)

        self.logger.info(f"Calculated real distances for {len(updated_hotels)} hotels using Amap")
        return updated_hotels

    async def _get_coordinates(self, address: str) -> Optional[str]:
        geocode = await amap_service.geocode(address)
        if geocode:
            return f"{geocode['longitude']},{geocode['latitude']}"
        return None

    def _search_hotels_in_city(self, city: str) -> List[dict]:
        return [
            {
                "id": h["id"],
                "name": h["name"],
                "stars": h["stars"],
                "price": h["price"],
                "city": h["city"],
                "district": h["district"],
                "address": h["address"],
                "location": h.get("location", ""),
                "distance_km": h["distance_km"],
                "facilities": h["facilities"]
            }
            for h in MOCK_HOTELS if h["city"] == city
        ]

    def _generate_hotel_recommendations(
        self,
        hotels: List[dict],
        budget_limit: float,
        is_compliant: bool
    ) -> List[dict]:
        recommendations = []
        for hotel in hotels:
            distance_km = hotel.get("real_distance_km", hotel.get("distance_km", 1.0))
            distance_info = self._get_distance_info(distance_km)
            transport_info = self._get_transport_info(distance_km)

            recommendations.append({
                "id": hotel["id"],
                "name": hotel["name"],
                "stars": hotel["stars"],
                "price": hotel["price"],
                "district": hotel["district"],
                "address": hotel["address"],
                "distance_km": round(distance_km, 1),
                "distance_info": distance_info,
                "transport_info": transport_info,
                "facilities": hotel["facilities"],
                "distance_source": hotel.get("distance_source", "mock"),
                "compliance": {
                    "is_compliant": is_compliant,
                    "limit": budget_limit,
                    "over_budget": hotel["price"] - budget_limit if not is_compliant else None
                }
            })
        return recommendations

    def _get_distance_info(self, distance_km: float) -> str:
        if distance_km <= 0.5:
            return "步行5分钟内"
        elif distance_km <= 1.0:
            return "步行10分钟内"
        elif distance_km <= 2.0:
            return "打车10分钟内"
        else:
            return f"距离{distance_km:.1f}公里"

    def _get_transport_info(self, distance_km: float) -> str:
        if distance_km <= 1.0:
            return "步行/地铁可达"
        elif distance_km <= 3.0:
            return "地铁+步行"
        else:
            return "建议打车出行"

    async def _simple_search(self, input_data: dict) -> dict:
        city = input_data.get("city")
        check_in = input_data.get("check_in")
        check_out = input_data.get("check_out")
        star = input_data.get("star")
        user_level = input_data.get("user_level", "基层员工")
        customer_location = input_data.get("customer_location", "")
        use_amap = input_data.get("use_amap", True)

        city_tier = knowledge_base.retrieve_city_tier(city)
        hotel_policy = knowledge_base.retrieve_policies("hotel", user_level)
        budget_limit = hotel_policy.get(city_tier, 400) if isinstance(hotel_policy, dict) else 400

        all_hotels = self._search_hotels_in_city(city)

        if use_amap and customer_location:
            all_hotels = await self._calculate_real_distances(all_hotels, customer_location)

        compliant_hotels = []
        alternative_hotels = []

        for hotel in all_hotels:
            if star and hotel["stars"] != star:
                continue
            is_compliant = hotel["price"] <= budget_limit
            hotel_data = self._generate_hotel_recommendations([hotel], budget_limit, is_compliant)
            if is_compliant:
                compliant_hotels.extend(hotel_data)
            else:
                alternative_hotels.extend(hotel_data)

        return {
            "status": "completed",
            "compliant_hotels": compliant_hotels,
            "alternative_hotels": alternative_hotels,
            "total_compliant": len(compliant_hotels),
            "total_alternative": len(alternative_hotels),
            "used_real_distance": use_amap and bool(customer_location)
        }

    async def book_hotel(self, input_data: dict) -> dict:
        option_id = input_data.get("option_id")
        booking_id = f"hotel_booking_{option_id}_{hash(option_id) % 10000}"

        return {
            "status": "confirmed",
            "booking_id": booking_id,
            "message": "酒店预订成功（Mock）"
        }