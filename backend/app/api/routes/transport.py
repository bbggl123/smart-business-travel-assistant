from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import json
from app.api.types import ApiResponse
from app.api.models import TransportOption
from app.utils.logger import logger

router = APIRouter(prefix="/api/transport", tags=["transport"])


MOCK_FLIGHTS = [
    {
        "id": "flight_001",
        "type": "flight",
        "provider": "中国国航",
        "flight_no": "CA1234",
        "departure_city": "北京",
        "departure_code": "PEK",
        "departure_time": "08:30",
        "arrival_city": "上海",
        "arrival_code": "PVG",
        "arrival_time": "10:45",
        "duration": "2小时15分钟",
        "price": 680.0
    },
    {
        "id": "flight_002",
        "type": "flight",
        "provider": "东方航空",
        "flight_no": "MU5678",
        "departure_city": "北京",
        "departure_code": "PEK",
        "departure_time": "14:20",
        "arrival_city": "上海",
        "arrival_code": "PVG",
        "arrival_time": "16:35",
        "duration": "2小时15分钟",
        "price": 720.0
    },
    {
        "id": "flight_003",
        "type": "flight",
        "provider": "南方航空",
        "flight_no": "CZ9012",
        "departure_city": "北京",
        "departure_code": "PEK",
        "departure_time": "19:00",
        "arrival_city": "上海",
        "arrival_code": "PVG",
        "arrival_time": "21:15",
        "duration": "2小时15分钟",
        "price": 580.0
    }
]

MOCK_TRAINS = [
    {
        "id": "train_001",
        "type": "train",
        "provider": "高铁",
        "train_no": "G101",
        "departure_city": "北京",
        "departure_code": "BJN",
        "departure_time": "07:00",
        "arrival_city": "上海",
        "arrival_code": "SHH",
        "arrival_time": "12:30",
        "duration": "5小时30分钟",
        "price": 553.0
    },
    {
        "id": "train_002",
        "type": "train",
        "provider": "高铁",
        "train_no": "G201",
        "departure_city": "北京",
        "departure_code": "BJN",
        "departure_time": "09:00",
        "arrival_city": "上海",
        "arrival_code": "SHH",
        "arrival_time": "14:30",
        "duration": "5小时30分钟",
        "price": 553.0
    },
    {
        "id": "train_003",
        "type": "train",
        "provider": "高铁",
        "train_no": "G301",
        "departure_city": "北京",
        "departure_code": "BJN",
        "departure_time": "11:00",
        "arrival_city": "上海",
        "arrival_code": "SHH",
        "arrival_time": "16:30",
        "duration": "5小时30分钟",
        "price": 553.0
    }
]


class TransportSearchRequest(BaseModel):
    departure: str
    destination: str
    date: str
    type: str = "both"


class TransportBookRequest(BaseModel):
    option_id: str


@router.post("/search")
async def search_transport(request: TransportSearchRequest):
    try:
        results = []

        if request.type in ["flight", "both"]:
            for flight in MOCK_FLIGHTS:
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
                    "price": flight["price"],
                    "compliance": {
                        "is_compliant": True,
                        "reason": None
                    }
                })

        if request.type in ["train", "both"]:
            for train in MOCK_TRAINS:
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
                    "price": train["price"],
                    "compliance": {
                        "is_compliant": True,
                        "reason": None
                    }
                })

        return ApiResponse(
            code=0,
            message="success",
            data=results
        )
    except Exception as e:
        logger.error(f"Transport search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/book")
async def book_transport(request: TransportBookRequest):
    try:
        booking_id = f"booking_{uuid.uuid4().hex[:8]}"

        return ApiResponse(
            code=0,
            message="success",
            data={
                "booking_id": booking_id,
                "status": "confirmed",
                "message": "预订成功（Mock）"
            }
        )
    except Exception as e:
        logger.error(f"Transport book error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
