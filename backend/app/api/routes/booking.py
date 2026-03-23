from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.booking import booking_service, BookingType, BookingStatus
from app.utils.logger import logger

router = APIRouter(prefix="/booking", tags=["booking"])


class TransportBookingRequest(BaseModel):
    option_data: dict
    user_info: dict


class HotelBookingRequest(BaseModel):
    option_data: dict
    user_info: dict
    stay_dates: dict


class DiningBookingRequest(BaseModel):
    option_data: dict
    user_info: dict
    dining_info: dict


class ConfirmBookingRequest(BaseModel):
    confirmation_data: Optional[dict] = None


class CancelBookingRequest(BaseModel):
    reason: Optional[str] = None


@router.post("/transport")
async def create_transport_booking(request: TransportBookingRequest):
    try:
        result = booking_service.create_transport_booking(
            option_data=request.option_data,
            user_info=request.user_info
        )
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Create transport booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hotel")
async def create_hotel_booking(request: HotelBookingRequest):
    try:
        result = booking_service.create_hotel_booking(
            option_data=request.option_data,
            user_info=request.user_info,
            stay_dates=request.stay_dates
        )
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Create hotel booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dining")
async def create_dining_booking(request: DiningBookingRequest):
    try:
        result = booking_service.create_dining_booking(
            option_data=request.option_data,
            user_info=request.user_info,
            dining_info=request.dining_info
        )
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Create dining booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/confirm")
async def confirm_booking(booking_id: str, request: ConfirmBookingRequest = None):
    try:
        confirmation_data = request.confirmation_data if request else None
        result = booking_service.confirm_booking(booking_id, confirmation_data)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirm booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: str, request: CancelBookingRequest = None):
    try:
        reason = request.reason if request else None
        result = booking_service.cancel_booking(booking_id, reason)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/complete")
async def complete_booking(booking_id: str, completion_data: dict = None):
    try:
        result = booking_service.complete_booking(booking_id, completion_data)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/retry")
async def retry_booking(booking_id: str):
    try:
        result = booking_service.retry_booking(booking_id)

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}")
async def get_booking(booking_id: str):
    try:
        result = booking_service.get_booking(booking_id)

        if not result:
            raise HTTPException(status_code=404, detail="Booking not found")

        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get booking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_bookings(
    status: Optional[str] = None,
    booking_type: Optional[str] = None,
    user_id: Optional[str] = None
):
    try:
        status_enum = BookingStatus(status) if status else None
        type_enum = BookingType(booking_type) if booking_type else None

        results = booking_service.list_bookings(
            status=status_enum,
            booking_type=type_enum,
            user_id=user_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "bookings": results,
                "count": len(results)
            }
        }
    except Exception as e:
        logger.error(f"List bookings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
