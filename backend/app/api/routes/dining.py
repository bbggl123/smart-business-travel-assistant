from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.api.types import ApiResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/dining", tags=["dining"])


MOCK_RESTAURANTS = [
    {
        "id": "restaurant_001",
        "restaurant": "上海老饭店",
        "cuisine": "本帮菜",
        "city": "上海",
        "address": "上海市黄浦区福佑路168号",
        "price_per_person": 200.0,
        "has_private_room": True,
        "recommended_dishes": [
            {"name": "蟹粉小笼", "price": 88.0, "suitable_for": 3},
            {"name": "红烧肉", "price": 68.0, "suitable_for": 4},
            {"name": "清炒虾仁", "price": 98.0, "suitable_for": 4},
            {"name": "松鼠鳜鱼", "price": 168.0, "suitable_for": 5}
        ]
    },
    {
        "id": "restaurant_002",
        "restaurant": "绿波廊",
        "cuisine": "本帮菜",
        "city": "上海",
        "address": "上海市黄浦区豫园路125号",
        "price_per_person": 180.0,
        "has_private_room": True,
        "recommended_dishes": [
            {"name": "蟹粉豆腐", "price": 78.0, "suitable_for": 3},
            {"name": "八宝辣酱", "price": 58.0, "suitable_for": 4},
            {"name": "水晶虾仁", "price": 108.0, "suitable_for": 4}
        ]
    },
    {
        "id": "restaurant_003",
        "restaurant": "鼎泰丰",
        "cuisine": "淮扬菜",
        "city": "上海",
        "address": "上海市黄浦区思南路38号",
        "price_per_person": 150.0,
        "has_private_room": False,
        "recommended_dishes": [
            {"name": "小笼包", "price": 68.0, "suitable_for": 4},
            {"name": "元盅焖排骨", "price": 78.0, "suitable_for": 3},
            {"name": "红油抄手", "price": 38.0, "suitable_for": 3}
        ]
    },
    {
        "id": "restaurant_004",
        "restaurant": "新荣记",
        "cuisine": "台州菜",
        "city": "上海",
        "address": "上海市静安区南京西路1266号",
        "price_per_person": 280.0,
        "has_private_room": True,
        "recommended_dishes": [
            {"name": "野生大黄鱼", "price": 388.0, "suitable_for": 5},
            {"name": "沙蒜豆面", "price": 128.0, "suitable_for": 4},
            {"name": "家烧苔菜", "price": 68.0, "suitable_for": 4}
        ]
    },
    {
        "id": "restaurant_005",
        "restaurant": "唐宫",
        "cuisine": "粤菜",
        "city": "上海",
        "address": "上海市浦东新区世纪大道100号",
        "price_per_person": 220.0,
        "has_private_room": True,
        "recommended_dishes": [
            {"name": "金奖乳鸽", "price": 58.0, "suitable_for": 3},
            {"name": "唐宫虾饺", "price": 48.0, "suitable_for": 4},
            {"name": "蜜汁叉烧", "price": 78.0, "suitable_for": 4}
        ]
    }
]


class DiningSearchRequest(BaseModel):
    city: str
    date: str
    headcount: int
    cuisine: Optional[str] = None
    budget_per_person: Optional[float] = None


class DiningReserveRequest(BaseModel):
    option_id: str


@router.post("/search")
async def search_dining(request: DiningSearchRequest):
    try:
        results = []

        for restaurant in MOCK_RESTAURANTS:
            if restaurant["city"] == request.city:
                if request.cuisine and restaurant["cuisine"] != request.cuisine:
                    continue
                if request.budget_per_person and restaurant["price_per_person"] > request.budget_per_person:
                    continue

                total_amount = restaurant["price_per_person"] * request.headcount
                is_compliant = restaurant["price_per_person"] <= 300

                results.append({
                    "id": restaurant["id"],
                    "restaurant": restaurant["restaurant"],
                    "cuisine": restaurant["cuisine"],
                    "city": restaurant["city"],
                    "address": restaurant["address"],
                    "price_per_person": restaurant["price_per_person"],
                    "headcount": request.headcount,
                    "total_amount": total_amount,
                    "has_private_room": restaurant["has_private_room"],
                    "recommended_dishes": restaurant["recommended_dishes"],
                    "compliance": {
                        "is_compliant": is_compliant,
                        "limit": 300.0,
                        "over_budget": restaurant["price_per_person"] - 300.0 if not is_compliant else None
                    }
                })

        return ApiResponse(
            code=0,
            message="success",
            data=results
        )
    except Exception as e:
        logger.error(f"Dining search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reserve")
async def reserve_dining(request: DiningReserveRequest):
    try:
        booking_id = f"dining_booking_{uuid.uuid4().hex[:8]}"

        return ApiResponse(
            code=0,
            message="success",
            data={
                "booking_id": booking_id,
                "status": "confirmed",
                "message": "餐厅预约成功（Mock）"
            }
        )
    except Exception as e:
        logger.error(f"Dining reserve error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
