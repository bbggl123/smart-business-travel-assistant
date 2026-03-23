from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.api.types import ApiResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/hotel", tags=["hotel"])


MOCK_HOTELS = [
    {
        "id": "hotel_001",
        "name": "上海外滩中心酒店",
        "stars": 5,
        "city": "上海",
        "district": "黄浦区",
        "address": "上海市黄浦区中山东一路100号",
        "price": 1200.0,
        "distance_km": 0.5,
        "facilities": ["免费WiFi", "健身房", "游泳池", "餐厅", "会议室"]
    },
    {
        "id": "hotel_002",
        "name": "上海静安香格里拉大酒店",
        "stars": 5,
        "city": "上海",
        "district": "静安区",
        "address": "上海市静安区延安中路1218号",
        "price": 1100.0,
        "distance_km": 1.2,
        "facilities": ["免费WiFi", "健身房", "SPA", "餐厅"]
    },
    {
        "id": "hotel_003",
        "name": "上海金茂君悦大酒店",
        "stars": 5,
        "city": "上海",
        "district": "浦东新区",
        "address": "上海市浦东新区世纪大道88号",
        "price": 1050.0,
        "distance_km": 2.0,
        "facilities": ["免费WiFi", "健身房", "游泳池", "餐厅"]
    },
    {
        "id": "hotel_004",
        "name": "上海豫园万丽酒店",
        "stars": 4,
        "city": "上海",
        "district": "黄浦区",
        "address": "上海市黄浦区河南南路158号",
        "price": 650.0,
        "distance_km": 1.5,
        "facilities": ["免费WiFi", "健身房", "餐厅"]
    },
    {
        "id": "hotel_005",
        "name": "上海浦东嘉里大酒店",
        "stars": 5,
        "city": "上海",
        "district": "浦东新区",
        "address": "上海市浦东新区花木路1388号",
        "price": 900.0,
        "distance_km": 3.5,
        "facilities": ["免费WiFi", "健身房", "游泳池", "儿童俱乐部", "餐厅"]
    },
    {
        "id": "hotel_006",
        "name": "上海虹桥金陵花园酒店",
        "stars": 4,
        "city": "上海",
        "district": "长宁区",
        "address": "上海市长宁区虹桥路2266号",
        "price": 550.0,
        "distance_km": 4.0,
        "facilities": ["免费WiFi", "健身房", "餐厅", "停车场"]
    }
]


class HotelSearchRequest(BaseModel):
    city: str
    check_in: str
    check_out: str
    star: Optional[int] = None


class HotelBookRequest(BaseModel):
    option_id: str


@router.post("/search")
async def search_hotel(request: HotelSearchRequest):
    try:
        results = []

        for hotel in MOCK_HOTELS:
            if hotel["city"] == request.city:
                if request.star is None or hotel["stars"] == request.star:
                    is_compliant = hotel["price"] <= 1200
                    results.append({
                        "id": hotel["id"],
                        "name": hotel["name"],
                        "stars": hotel["stars"],
                        "price": hotel["price"],
                        "city": hotel["city"],
                        "district": hotel["district"],
                        "address": hotel["address"],
                        "distance_km": hotel["distance_km"],
                        "facilities": hotel["facilities"],
                        "compliance": {
                            "is_compliant": is_compliant,
                            "limit": 1200.0,
                            "over_budget": hotel["price"] - 1200.0 if not is_compliant else None
                        }
                    })

        return ApiResponse(
            code=0,
            message="success",
            data=results
        )
    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book")
async def book_hotel(request: HotelBookRequest):
    try:
        booking_id = f"hotel_booking_{uuid.uuid4().hex[:8]}"

        return ApiResponse(
            code=0,
            message="success",
            data={
                "booking_id": booking_id,
                "status": "confirmed",
                "message": "酒店预订成功（Mock）"
            }
        )
    except Exception as e:
        logger.error(f"Hotel book error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
