from app.agents.base import BaseAgent
from app.cot.base import COTLayerResult, COTResult
from typing import Dict, List, Any
from app.utils.logger import logger
import json
import random
import subprocess
import os


SKILL_DIR = "/workspace/web-content-fetcher-main"
FETCH_SCRIPT = os.path.join(SKILL_DIR, "scripts", "fetch.py")


MOCK_FLIGHTS_TEMPLATE = [
    {"flight_no": "CA1234", "provider": "中国国航", "departure_city": "北京", "arrival_city": "上海", "base_price": 680},
    {"flight_no": "MU5678", "provider": "东方航空", "departure_city": "北京", "arrival_city": "上海", "base_price": 720},
    {"flight_no": "CZ3089", "provider": "南方航空", "departure_city": "北京", "arrival_city": "广州", "base_price": 1200},
]

MOCK_HOTELS_TEMPLATE = [
    {"name": "外滩中心酒店", "stars": 5, "city": "上海", "base_price": 1100},
    {"name": "静安香格里拉", "stars": 5, "city": "上海", "base_price": 1050},
    {"name": "金茂君悦", "stars": 5, "city": "上海", "base_price": 1000},
    {"name": "豫园万丽", "stars": 4, "city": "上海", "base_price": 650},
]

MOCK_RESTAURANTS_TEMPLATE = [
    {"restaurant": "上海老饭店", "cuisine": "本帮菜", "city": "上海", "base_price": 200},
    {"restaurant": "绿波廊", "cuisine": "本帮菜", "city": "上海", "base_price": 180},
    {"restaurant": "新荣记", "cuisine": "台州菜", "city": "上海", "base_price": 280},
]


class MockDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("MockDataAgent")

    async def process(self, input_data: dict) -> dict:
        if self.enable_cot:
            return await self.process_with_cot(input_data)

        action = input_data.get("action", "generate")
        if action == "generate":
            return await self._simple_generate(input_data)
        elif action == "fetch":
            return await self._simple_fetch(input_data)
        elif action == "fetch_url":
            return await self._fetch_url(input_data)
        return {"status": "error", "message": f"Unknown action: {action}"}

    async def process_with_cot(self, input_data: dict) -> dict:
        cot_result = COTResult(
            request_id=f"mock_{id(input_data)}",
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
            self.logger.error(f"MockDataAgent COT error: {e}")
            import traceback
            traceback.print_exc()
            fallback = await self._simple_generate(input_data)
            fallback["cot_error"] = str(e)
            return fallback

    async def intent_understanding_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        data_type = input_data.get("data_type", "flight")
        count = input_data.get("count", 10)
        use_real_data = input_data.get("use_real_data", False)

        reasoning_steps = [
            f"解析Mock数据生成请求",
            f"数据类型: {data_type}",
            f"生成数量: {count}条",
            f"使用真实数据: {'是' if use_real_data else '否'}"
        ]

        return COTLayerResult(
            layer_name="intent_understanding",
            input_data=input_data,
            output_data={
                "data_type": data_type,
                "count": count,
                "use_real_data": use_real_data,
                "action": "generate_mock_data"
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def knowledge_retrieval_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        data_type = input_data.get("data_type", "flight")
        use_real_data = input_data.get("use_real_data", False)

        templates = {
            "flight": MOCK_FLIGHTS_TEMPLATE,
            "hotel": MOCK_HOTELS_TEMPLATE,
            "restaurant": MOCK_RESTAURANTS_TEMPLATE
        }

        template = templates.get(data_type, MOCK_FLIGHTS_TEMPLATE)

        fetch_urls = self._get_fetch_urls(data_type)

        reasoning_steps = [
            f"检索数据模板: {data_type}",
            f"模板数量: {len(template)}",
            f"使用真实数据: {'是' if use_real_data else '否'}",
            f"待抓取URL数量: {len(fetch_urls)}" if fetch_urls else "无待抓取URL"
        ]

        return COTLayerResult(
            layer_name="knowledge_retrieval",
            input_data=input_data,
            output_data={
                "template": template,
                "data_type": data_type,
                "fetch_urls": fetch_urls,
                "use_real_data": use_real_data
            },
            reasoning_steps=reasoning_steps,
            confidence=0.95
        )

    async def reasoning_decision_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        knowledge = input_data.get("knowledge_retrieval_output", {})
        template = knowledge.get("template", [])
        count = input_data.get("count", 10)
        use_real_data = knowledge.get("use_real_data", False)
        data_type = knowledge.get("data_type", "flight")

        real_data = []
        if use_real_data:
            fetch_urls = knowledge.get("fetch_urls", [])
            for url in fetch_urls[:3]:
                content = await self._fetch_web_content(url)
                if content:
                    parsed = self._parse_content(content, data_type)
                    real_data.extend(parsed)

        variants = self._generate_variants(template, max(count - len(real_data), 0))
        all_data = real_data + variants

        reasoning_steps = [
            f"生成{count}条Mock数据",
            f"使用{len(template)}个模板",
            f"真实数据抓取: {len(real_data)}条",
            f"Mock数据生成: {len(variants)}条",
            f"总计: {len(all_data)}条"
        ]

        return COTLayerResult(
            layer_name="reasoning_decision",
            input_data=input_data,
            output_data={
                "variants": variants,
                "real_data": real_data,
                "all_data": all_data,
                "total_count": len(all_data)
            },
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    async def response_generation_layer(self, input_data: dict, cot_result: COTResult) -> COTLayerResult:
        reasoning = input_data.get("reasoning_decision_output", {})
        all_data = reasoning.get("all_data", [])

        response_data = {
            "status": "completed",
            "data": all_data,
            "count": len(all_data),
            "format": "json"
        }

        reasoning_steps = [
            f"生成Mock数据集",
            f"数据条数: {len(all_data)}",
            f"数据格式: JSON"
        ]

        return COTLayerResult(
            layer_name="response_generation",
            input_data=input_data,
            output_data=response_data,
            reasoning_steps=reasoning_steps,
            confidence=0.9
        )

    def _get_fetch_urls(self, data_type: str) -> List[str]:
        urls = {
            "flight": [
                "https://flights.ctrip.com/international/flights/pekg-pvg.html",
                "https://flights.ctrip.com/international/flights/beijing-shanghai/"
            ],
            "hotel": [
                "https://hotels.ctrip.com/hotels/list?q=上海",
                "https://hotels.ctrip.com/hotels/list?q=北京"
            ],
            "restaurant": [
                "https://www.dianping.com/search/keyword/1/0/%E4%B8%8A%E6%B5%B7",
                "https://www.dianping.com/search/keyword/1/0/%E5%8C%97%E4%BA%AC"
            ]
        }
        return urls.get(data_type, [])

    async def _fetch_web_content(self, url: str, max_chars: int = 30000) -> str:
        try:
            cmd = f'python "{FETCH_SCRIPT}" "{url}" {max_chars}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                self.logger.info(f"Successfully fetched content from {url}")
                return result.stdout
            else:
                self.logger.warning(f"Failed to fetch {url}: {result.stderr}")
                return ""
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return ""

    def _parse_content(self, content: str, data_type: str) -> List[dict]:
        import re
        parsed = []
        
        if data_type == "flight":
            flight_patterns = [
                r'([A-Z]{2}[0-9]{3,4})\s*[:：]?\s*([^\s,<]+)\s*→\s*([^\s,<]+)',
                r'([A-Z]{2}[0-9]{3,4})[\s-]*([^\n,<]{2,8})[\s-]*([^\n,<]{2,8})',
                r'航班[：:]?\s*([A-Z]{2}[0-9]{3,4})',
            ]
            for pattern in flight_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:5]:
                    if len(match) >= 3:
                        parsed.append({
                            "source": "web_content",
                            "data_type": "flight",
                            "flight_no": match[0] if match[0] else match[1] if len(match) > 1 else "Unknown",
                            "provider": "待确认",
                            "departure_city": match[1] if len(match) > 1 else "待确认",
                            "arrival_city": match[2] if len(match) > 2 else "待确认",
                            "base_price": 0,
                            "content_preview": content[:200]
                        })
            if not parsed:
                parsed.append({
                    "source": "web_content",
                    "data_type": "flight",
                    "content_preview": content[:500]
                })
        
        elif data_type == "hotel":
            hotel_patterns = [
                r'([^\n,<]{2,10})酒店[^\n,<]{0,20}(?:¥|价格|price)[:：]?\s*(\d+)',
                r'([^\n,<]{2,10})[^\n,<]{0,10}(?:五星|四星|三星|豪华|舒适)',
            ]
            for pattern in hotel_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:5]:
                    if match:
                        name = match[0].strip() if isinstance(match, tuple) else match
                        price = int(match[1]) if isinstance(match, tuple) and len(match) > 1 and match[1].isdigit() else 0
                        parsed.append({
                            "source": "web_content",
                            "data_type": "hotel",
                            "name": name if name else "待确认酒店",
                            "stars": 0,
                            "base_price": price,
                            "content_preview": content[:200]
                        })
            if not parsed:
                parsed.append({
                    "source": "web_content",
                    "data_type": "hotel",
                    "content_preview": content[:500]
                })
        
        elif data_type == "restaurant":
            rest_patterns = [
                r'([^\n,<]{2,10})(?:餐厅|饭店|菜馆)[^\n,<]{0,30}(?:¥|价格|人均)[:：]?\s*(\d+)',
                r'([^\n,<]{2,10})[^\n,<]{0,20}(?:川菜|粤菜|湘菜|火锅|日料|西餐)',
            ]
            for pattern in rest_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:5]:
                    if match:
                        name = match[0].strip() if isinstance(match, tuple) else match
                        price = int(match[1]) if isinstance(match, tuple) and len(match) > 1 and str(match[1]).isdigit() else 0
                        parsed.append({
                            "source": "web_content",
                            "data_type": "restaurant",
                            "restaurant": name if name else "待确认餐厅",
                            "cuisine": "待确认",
                            "base_price": price,
                            "content_preview": content[:200]
                        })
            if not parsed:
                parsed.append({
                    "source": "web_content",
                    "data_type": "restaurant",
                    "content_preview": content[:500]
                })
        
        return parsed

    def _generate_variants(self, template: List[dict], count: int) -> List[dict]:
        if count <= 0:
            return []
        variants = []
        for i in range(count):
            template_item = template[i % len(template)] if template else {}
            variant = self._create_variant(template_item, i)
            variants.append(variant)
        return variants

    def _create_variant(self, template: dict, index: int) -> dict:
        variant = template.copy()

        if "flight_no" in variant:
            variant["id"] = f"flight_{index}"
            variant["departure_time"] = f"{8 + index % 10}:{random.choice(['00', '30'])}"
            variant["arrival_time"] = f"{11 + index % 6}:{random.choice(['00', '30'])}"
            variant["price"] = template.get("base_price", 500) + random.randint(-100, 200)
            variant["duration"] = f"{2 + random.randint(0, 3)}小时{random.randint(0, 59)}分钟"

        elif "name" in variant and "stars" in variant:
            variant["id"] = f"hotel_{index}"
            variant["price"] = template.get("base_price", 500) + random.randint(-200, 300)
            variant["distance_km"] = round(random.uniform(0.5, 5.0), 1)
            variant["facilities"] = random.sample(
                ["免费WiFi", "健身房", "游泳池", "餐厅", "会议室", "SPA"],
                k=random.randint(2, 5)
            )

        elif "restaurant" in variant:
            variant["id"] = f"restaurant_{index}"
            variant["price_per_person"] = template.get("base_price", 150) + random.randint(-30, 80)
            variant["address"] = f"{template.get('city', '上海')}{random.choice(['黄浦区', '静安区', '浦东新区'])}XX路{random.randint(1, 500)}号"
            variant["has_private_room"] = random.choice([True, False])

        return variant

    async def _simple_generate(self, input_data: dict) -> dict:
        data_type = input_data.get("data_type", "flight")
        count = input_data.get("count", 10)
        use_real_data = input_data.get("use_real_data", False)

        templates = {
            "flight": MOCK_FLIGHTS_TEMPLATE,
            "hotel": MOCK_HOTELS_TEMPLATE,
            "restaurant": MOCK_RESTAURANTS_TEMPLATE
        }

        template = templates.get(data_type, MOCK_FLIGHTS_TEMPLATE)

        real_data = []
        if use_real_data:
            fetch_urls = self._get_fetch_urls(data_type)
            for url in fetch_urls[:3]:
                content = await self._fetch_web_content(url)
                if content:
                    parsed = self._parse_content(content, data_type)
                    real_data.extend(parsed)

        variants = self._generate_variants(template, max(count - len(real_data), 0))
        all_data = real_data + variants

        return {
            "status": "completed",
            "data_type": data_type,
            "data": all_data,
            "count": len(all_data),
            "real_data_count": len(real_data),
            "mock_data_count": len(variants)
        }

    async def _simple_fetch(self, input_data: dict) -> dict:
        data_type = input_data.get("data_type", "flight")
        fetch_urls = self._get_fetch_urls(data_type)

        results = []
        for url in fetch_urls:
            content = await self._fetch_web_content(url)
            if content:
                results.append({
                    "url": url,
                    "status": "success",
                    "length": len(content)
                })
            else:
                results.append({
                    "url": url,
                    "status": "error",
                    "message": "Failed to fetch content"
                })

        return {
            "status": "completed",
            "data_type": data_type,
            "fetch_results": results
        }

    async def _fetch_url(self, input_data: dict) -> dict:
        url = input_data.get("url", "")
        if not url:
            return {"status": "error", "message": "URL is required"}

        content = await self._fetch_web_content(url)
        if content:
            return {
                "status": "success",
                "url": url,
                "content": content,
                "length": len(content)
            }
        else:
            return {
                "status": "error",
                "url": url,
                "message": "Failed to fetch content"
            }

    async def fetch_real_flights(self, route: dict) -> List[dict]:
        content = await self._fetch_web_content("https://flights.ctrip.com")
        if content:
            return self._parse_content(content, "flight")
        return []

    async def fetch_real_hotels(self, city: str, check_in: str, check_out: str) -> List[dict]:
        content = await self._fetch_web_content(f"https://www.ctrip.com/hotels/{city}")
        if content:
            return self._parse_content(content, "hotel")
        return []

    async def fetch_real_restaurants(self, city: str, cuisine: str = None) -> List[dict]:
        content = await self._fetch_web_content(f"https://www.dianping.com/{city}")
        if content:
            return self._parse_content(content, "restaurant")
        return []

    async def export_to_json(self, dataset: List[dict], filename: str) -> str:
        return json.dumps(dataset, ensure_ascii=False, indent=2)