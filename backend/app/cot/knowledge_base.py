from typing import Dict, List, Any, Optional
from app.utils.logger import logger
import json


class KnowledgeBase:
    def __init__(self):
        self.travel_policies = self._init_travel_policies()
        self.city_tiers = self._init_city_tiers()
        self.level_rules = self._init_level_rules()
        self.history_cases: List[dict] = []

    def _init_travel_policies(self) -> dict:
        return {
            "flight_rules": {
                "基层员工": {
                    "description": "经济舱折扣票，里程≥1000km且高铁时长≥6小时",
                    "max_price": 1000,
                    "cabin": "经济舱折扣票"
                },
                "主管/资深专员": {
                    "description": "经济舱，里程≥800km且高铁时长≥5小时",
                    "max_price": 1500,
                    "cabin": "经济舱"
                },
                "经理级": {
                    "description": "经济舱/高端经济舱，无里程限制",
                    "max_price": 2000,
                    "cabin": "经济舱/高端经济舱"
                },
                "总监级": {
                    "description": "商务舱折扣票，时长≥8小时或月度出差≥4次",
                    "max_price": 3000,
                    "cabin": "商务舱折扣票"
                },
                "副总/高管": {
                    "description": "商务舱/头等舱，无限制",
                    "max_price": 5000,
                    "cabin": "商务舱/头等舱"
                }
            },
            "train_rules": {
                "基层员工": {"seat": "二等座", "description": "标准配置"},
                "主管/资深专员": {"seat": "二等座（一等座需申请）", "description": "时长≥8小时可申请一等座"},
                "经理级": {"seat": "一等座", "description": "时长≥10小时可申请商务座"},
                "总监级": {"seat": "一等座/商务座", "description": "无限制"},
                "副总/高管": {"seat": "一等座/商务座", "description": "无限制"}
            },
            "hotel_rules": {
                level: {
                    city_tier: price
                    for city_tier, price in zip(
                        ["一线", "新一线", "二线", "其他"],
                        prices
                    )
                }
                for level, prices in zip(
                    ["基层员工", "主管/资深专员", "经理级", "总监级", "副总/高管"],
                    [
                        [400, 350, 300, 260],
                        [500, 450, 400, 350],
                        [650, 600, 550, 500],
                        [800, 750, 700, 650],
                        [1200, 1000, 900, 800]
                    ]
                )
            },
            "dining_rules": {
                "一线": 300,
                "新一线": 260,
                "其他": 200
            },
            "subsidy_rules": {
                "通讯补贴": {"境内": 50, "境外": 80},
                "偏远地区": {"补贴金额": 50, "地区": ["西藏", "新疆", "青海"]},
                "节假日": {"补贴金额": 100},
                "夜间抵达": {"补贴金额": 30, "时间": "22:00后"}
            }
        }

    def _init_city_tiers(self) -> dict:
        return {
            "一线": ["北京", "上海", "广州", "深圳"],
            "新一线": [
                "杭州", "成都", "重庆", "武汉", "南京", "西安", "长沙",
                "苏州", "天津", "东莞", "青岛", "沈阳", "郑州", "昆明"
            ],
            "二线": [
                "大连", "厦门", "无锡", "合肥", "福州", "哈尔滨", "济南",
                "温州", "南宁", "长春", "徐州", "泉州", "石家庄", "贵阳",
                "太原", "常州", "南通", "嘉兴", "惠州", "金华", "珠海", "中山"
            ]
        }

    def _init_level_rules(self) -> dict:
        return {
            "基层员工": {
                "aliases": ["专员", "助理", "员工"],
                "approval_chain": ["直属主管", "部门经理"],
                "max_approval_amount": 5000
            },
            "主管/资深专员": {
                "aliases": ["主管", "资深专员", "高级专员"],
                "approval_chain": ["部门经理", "总监"],
                "max_approval_amount": 10000
            },
            "经理级": {
                "aliases": ["经理", "部门经理", "项目经理"],
                "approval_chain": ["总监", "分管副总"],
                "max_approval_amount": 20000
            },
            "总监级": {
                "aliases": ["总监", "高级总监"],
                "approval_chain": ["分管副总", "总经理"],
                "max_approval_amount": 50000
            },
            "副总/高管": {
                "aliases": ["副总", "副总裁", "高管", "CXO"],
                "approval_chain": ["总经理", "董事长"],
                "max_approval_amount": 100000
            }
        }

    def retrieve_policies(self, category: str, level: Optional[str] = None) -> dict:
        if category == "flight":
            policies = self.travel_policies.get("flight_rules", {})
            if level:
                return policies.get(level, {})
            return policies
        elif category == "train":
            policies = self.travel_policies.get("train_rules", {})
            if level:
                return policies.get(level, {})
            return policies
        elif category == "hotel":
            policies = self.travel_policies.get("hotel_rules", {})
            if level:
                return policies.get(level, {})
            return policies
        elif category == "dining":
            return self.travel_policies.get("dining_rules", {})
        elif category == "subsidy":
            return self.travel_policies.get("subsidy_rules", {})
        return {}

    def retrieve_city_tier(self, city: str) -> str:
        for tier, cities in self.city_tiers.items():
            if city in cities:
                return tier
        return "其他"

    def retrieve_level_info(self, level: str) -> dict:
        for level_key, info in self.level_rules.items():
            if level in info.get("aliases", []) or level == level_key:
                return {
                    "level": level_key,
                    "approval_chain": info["approval_chain"],
                    "max_approval_amount": info["max_approval_amount"]
                }
        return {
            "level": "基层员工",
            "approval_chain": ["直属主管", "部门经理"],
            "max_approval_amount": 5000
        }

    def retrieve_relevant_knowledge(
        self,
        entities: dict,
        missing_fields: List[str]
    ) -> dict:
        knowledge = {
            "policies": {},
            "city_tier": None,
            "level_info": {},
            "suggestions": []
        }

        if "destination" in entities or "city" in entities:
            city = entities.get("destination") or entities.get("city")
            knowledge["city_tier"] = self.retrieve_city_tier(city)
            knowledge["policies"]["dining"] = self.travel_policies["dining_rules"].get(
                knowledge["city_tier"], 200
            )

        if "user_level" in entities:
            level = entities["user_level"]
            knowledge["level_info"] = self.retrieve_level_info(level)
            knowledge["policies"]["flight"] = self.retrieve_policies("flight", level)
            knowledge["policies"]["train"] = self.retrieve_policies("train", level)
            knowledge["policies"]["hotel"] = self.retrieve_policies("hotel", level)

            city = entities.get("destination") or entities.get("city", "一线")
            tier = self.retrieve_city_tier(city)
            knowledge["policies"]["hotel"] = self.travel_policies["hotel_rules"].get(level, {}).get(tier, 400)

        for field in missing_fields:
            if field == "user_level":
                knowledge["suggestions"].append("职级影响交通、住宿、餐饮的差旅标准")
            elif field == "destination":
                knowledge["suggestions"].append("目的地城市影响住宿和餐饮的差旅标准")
            elif field == "start_date":
                knowledge["suggestions"].append("出发日期影响航班和酒店的选择")
            elif field == "headcount":
                knowledge["suggestions"].append("人数影响酒店房间数量和餐厅预订")

        return knowledge

    def add_history_case(self, case: dict):
        self.history_cases.append(case)
        if len(self.history_cases) > 100:
            self.history_cases = self.history_cases[-100:]

    def get_similar_cases(self, entities: dict, limit: int = 3) -> List[dict]:
        if not self.history_cases:
            return []

        similar = []
        for case in self.history_cases:
            score = 0
            if entities.get("destination") == case.get("destination"):
                score += 2
            if entities.get("user_level") == case.get("user_level"):
                score += 2
            if entities.get("purpose") == case.get("purpose"):
                score += 1
            if score > 0:
                similar.append({"case": case, "score": score})

        similar.sort(key=lambda x: x["score"], reverse=True)
        return [s["case"] for s in similar[:limit]]


knowledge_base = KnowledgeBase()