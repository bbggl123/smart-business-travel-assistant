from typing import Optional, List, Dict, Any
from app.utils.logger import logger
import httpx
import json
import re


class WebFetcherService:
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

    async def fetch_url(self, url: str, timeout: int = 30) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Fetched URL: {url}, Status: {response.status_code}")
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None

    async def fetch_flights_ctrip(self, departure: str, arrival: str, date: str) -> List[dict]:
        url = f"https://www.ctrip.com/flight/{departure}-{arrival}.html?depdate={date}"
        html = await self.fetch_url(url)
        if not html:
            return []

        flights = self._parse_flight_html(html, departure, arrival)
        logger.info(f"Parsed {len(flights)} flights from Ctrip")
        return flights

    async def fetch_flights_12306(self, departure: str, arrival: str, date: str) -> List[dict]:
        url = f"https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={date}&leftTicketDTO.from_station={departure}&leftTicketDTO.to_station={arrival}&purpose_codes=ADULT"
        headers = {**self.headers, "Referer": "https://kyfw.12306.cn/otn/leftTicket/init"}
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                data = response.json()
                return self._parse_12306_trains(data)
        except Exception as e:
            logger.error(f"Failed to fetch 12306: {e}")
            return []

    async def fetch_hotels_amap(self, city: str, keywords: str = "") -> List[dict]:
        from app.services.amap import amap_service
        pois = await amap_service.search_hotels(city, keywords)
        hotels = [
            {
                "id": f"hotel_{i}",
                "name": poi.name,
                "address": poi.address,
                "city": city,
                "location": poi.location,
                "type": poi.type
            }
            for i, poi in enumerate(pois)
        ]
        logger.info(f"Fetched {len(hotels)} hotels from Amap for {city}")
        return hotels

    async def fetch_restaurants_amap(self, city: str, cuisine: str = "") -> List[dict]:
        from app.services.amap import amap_service
        pois = await amap_service.search_restaurants(city, cuisine)
        restaurants = [
            {
                "id": f"restaurant_{i}",
                "name": poi.name,
                "address": poi.address,
                "city": city,
                "cuisine": cuisine,
                "location": poi.location
            }
            for i, poi in enumerate(pois)
        ]
        logger.info(f"Fetched {len(restaurants)} restaurants from Amap for {city}")
        return restaurants

    def _parse_flight_html(self, html: str, departure: str, arrival: str) -> List[dict]:
        flights = []
        pattern = r'data-departure="([^"]+)"[^>]*data-arrival="([^"]+)"[^>]*data-price="(\d+)"'
        matches = re.findall(pattern, html)
        for i, (dep, arr, price) in enumerate(matches[:10]):
            flights.append({
                "id": f"flight_{i}",
                "departure": dep,
                "arrival": arr,
                "price": int(price),
                "source": "ctrip"
            })
        return flights

    def _parse_12306_trains(self, data: dict) -> List[dict]:
        trains = []
        try:
            result = data.get("data", {}).get("result", [])
            for item in result[:10]:
                parts = item.split("|")
                if len(parts) > 11:
                    trains.append({
                        "id": f"train_{len(trains)}",
                        "train_no": parts[3],
                        "departure": parts[6],
                        "arrival": parts[7],
                        "duration": parts[8],
                        "price": parts[10] if parts[10] != "null" else "无",
                        "source": "12306"
                    })
        except Exception as e:
            logger.error(f"Failed to parse 12306 data: {e}")
        return trains

    async def skill_invoke(self, action: str, params: dict) -> dict:
        if action == "fetch_flights":
            departure = params.get("departure", "")
            arrival = params.get("arrival", "")
            date = params.get("date", "")
            source = params.get("source", "ctrip")

            if source == "12306":
                data = await self.fetch_flights_12306(departure, arrival, date)
            else:
                data = await self.fetch_flights_ctrip(departure, arrival, date)

            return {
                "status": "success",
                "action": action,
                "count": len(data),
                "data": data
            }

        elif action == "fetch_hotels":
            city = params.get("city", "")
            keywords = params.get("keywords", "")
            data = await self.fetch_hotels_amap(city, keywords)

            return {
                "status": "success",
                "action": action,
                "count": len(data),
                "data": data
            }

        elif action == "fetch_restaurants":
            city = params.get("city", "")
            cuisine = params.get("cuisine", "")
            data = await self.fetch_restaurants_amap(city, cuisine)

            return {
                "status": "success",
                "action": action,
                "count": len(data),
                "data": data
            }

        elif action == "fetch_url":
            url = params.get("url", "")
            content = await self.fetch_url(url)

            return {
                "status": "success" if content else "error",
                "action": action,
                "content": content[:1000] if content else None,
                "length": len(content) if content else 0
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }


web_fetcher_service = WebFetcherService()