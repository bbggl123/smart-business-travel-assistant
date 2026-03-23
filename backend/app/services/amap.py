from typing import Optional, List, Dict, Any
from app.utils.logger import logger
import httpx
import json
from app.config import settings as config


class AmapPOI:
    def __init__(self, name: str = "", address: str = "", location: str = "",
                 city: str = "", type: str = "", distance: int = 0):
        self.name = name
        self.address = address
        self.location = location
        self.city = city
        self.type = type
        self.distance = distance

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "address": self.address,
            "location": self.location,
            "city": self.city,
            "type": self.type,
            "distance": self.distance
        }


class AmapService:
    def __init__(self):
        self.api_key = config.amap_api_key
        self.base_url = "https://restapi.amap.com/v3"

    async def search_nearby(
        self,
        location: str,
        keywords: str,
        types: Optional[str] = None,
        radius: int = 3000,
        city: Optional[str] = None
    ) -> List[AmapPOI]:
        url = f"{self.base_url}/place/around"
        params = {
            "key": self.api_key,
            "location": location,
            "keywords": keywords,
            "radius": radius,
            "output": "json"
        }
        if types:
            params["types"] = types
        if city:
            params["city"] = city

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1" and data.get("pois"):
                    pois = []
                    for poi in data["pois"]:
                        pois.append(AmapPOI(
                            name=poi.get("name", ""),
                            address=poi.get("address", ""),
                            location=poi.get("location", ""),
                            city=poi.get("cityname", ""),
                            type=poi.get("type", ""),
                            distance=int(poi.get("distance", 0))
                        ))
                    logger.info(f"Amap nearby search found {len(pois)} POIs")
                    return pois
                else:
                    logger.warning(f"Amap search failed: {data.get('info', 'Unknown error')}")
                    return []
        except Exception as e:
            logger.error(f"Amap search error: {e}")
            return []

    async def search_hotels(
        self,
        city: str,
        keywords: Optional[str] = None,
        star: Optional[str] = None
    ) -> List[AmapPOI]:
        url = f"{self.base_url}/place/text"
        params = {
            "key": self.api_key,
            "city": city,
            "keywords": keywords or "酒店",
            "types": "住宿服务",
            "output": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1" and data.get("pois"):
                    pois = []
                    for poi in data["pois"]:
                        location = poi.get("location", "")
                        pois.append(AmapPOI(
                            name=poi.get("name", ""),
                            address=poi.get("address", ""),
                            location=location,
                            city=poi.get("cityname", ""),
                            type=poi.get("type", "")
                        ))
                    logger.info(f"Amap hotel search found {len(pois)} hotels")
                    return pois
                else:
                    logger.warning(f"Amap hotel search failed: {data.get('info', 'Unknown error')}")
                    return []
        except Exception as e:
            logger.error(f"Amap hotel search error: {e}")
            return []

    async def search_restaurants(
        self,
        city: str,
        keywords: Optional[str] = None,
        cuisine: Optional[str] = None
    ) -> List[AmapPOI]:
        url = f"{self.base_url}/place/text"
        search_keywords = keywords or "餐厅"
        if cuisine:
            search_keywords = f"{cuisine} {search_keywords}"

        params = {
            "key": self.api_key,
            "city": city,
            "keywords": search_keywords,
            "types": "餐饮服务",
            "output": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1" and data.get("pois"):
                    pois = []
                    for poi in data["pois"]:
                        pois.append(AmapPOI(
                            name=poi.get("name", ""),
                            address=poi.get("address", ""),
                            location=poi.get("location", ""),
                            city=poi.get("cityname", ""),
                            type=poi.get("type", "")
                        ))
                    logger.info(f"Amap restaurant search found {len(pois)} restaurants")
                    return pois
                else:
                    logger.warning(f"Amap restaurant search failed: {data.get('info', 'Unknown error')}")
                    return []
        except Exception as e:
            logger.error(f"Amap restaurant search error: {e}")
            return []

    async def get_distance(
        self,
        origin: str,
        destination: str,
        mode: str = "walking"
    ) -> Optional[int]:
        url = f"{self.base_url}/direction/{mode}"
        params = {
            "key": self.api_key,
            "origin": origin,
            "destination": destination
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1":
                    route = data.get("route", {})
                    paths = route.get("paths", [])
                    if paths:
                        distance = int(paths[0].get("distance", 0))
                        logger.info(f"Distance from {origin} to {destination}: {distance}m")
                        return distance
                logger.warning(f"Amap distance query failed: {data.get('info', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Amap distance error: {e}")
            return None

    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[Dict[str, float]]:
        url = f"{self.base_url}/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address,
            "output": "json"
        }
        if city:
            params["city"] = city

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1" and data.get("geocodes"):
                    geocode = data["geocodes"][0]
                    location = geocode.get("location", "").split(",")
                    if len(location) == 2:
                        logger.info(f"Geocoded {address} to {location}")
                        return {
                            "longitude": float(location[0]),
                            "latitude": float(location[1])
                        }
                logger.warning(f"Amap geocode failed: {data.get('info', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Amap geocode error: {e}")
            return None

    async def regeocode(self, location: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/geocode/regeo"
        params = {
            "key": self.api_key,
            "location": location,
            "output": "json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("status") == "1":
                    regeocode = data.get("regeocode", {})
                    address_component = regeocode.get("addressComponent", {})

                    result = {
                        "formatted_address": regeocode.get("formatted_address", ""),
                        "province": address_component.get("province", ""),
                        "city": address_component.get("city", []),
                        "district": address_component.get("district", ""),
                        "location": location
                    }
                    logger.info(f"Regeocoded {location}: {result['formatted_address']}")
                    return result
                logger.warning(f"Amap regeocode failed: {data.get('info', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"Amap regeocode error: {e}")
            return None


amap_service = AmapService()