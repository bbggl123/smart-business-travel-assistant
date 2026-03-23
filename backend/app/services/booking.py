from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
from datetime import datetime
from app.utils.logger import logger


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class BookingType(str, Enum):
    TRANSPORT = "transport"
    HOTEL = "hotel"
    DINING = "dining"


class BookingStateMachine:
    def __init__(self, booking_id: str, booking_type: BookingType, initial_data: dict):
        self.booking_id = booking_id
        self.booking_type = booking_type
        self.status = BookingStatus.PENDING
        self.data = initial_data
        self.history = [
            {
                "status": BookingStatus.PENDING,
                "timestamp": datetime.now().isoformat(),
                "event": "created"
            }
        ]

    def can_transition(self, new_status: BookingStatus) -> bool:
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED, BookingStatus.FAILED],
            BookingStatus.CONFIRMED: [BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.FAILED],
            BookingStatus.COMPLETED: [],
            BookingStatus.CANCELLED: [],
            BookingStatus.FAILED: [BookingStatus.PENDING]
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition(self, new_status: BookingStatus, reason: str = None) -> bool:
        if not self.can_transition(new_status):
            logger.warning(f"Invalid transition: {self.status} -> {new_status}")
            return False

        old_status = self.status
        self.status = new_status

        self.history.append({
            "status": new_status,
            "timestamp": datetime.now().isoformat(),
            "event": "transition",
            "reason": reason,
            "from_status": old_status
        })

        logger.info(f"Booking {self.booking_id}: {old_status} -> {new_status}")
        return True

    def to_dict(self) -> dict:
        return {
            "booking_id": self.booking_id,
            "booking_type": self.booking_type,
            "status": self.status,
            "data": self.data,
            "history": self.history
        }


class BookingService:
    def __init__(self):
        self._bookings: Dict[str, BookingStateMachine] = {}

    def create_transport_booking(self, option_data: dict, user_info: dict) -> dict:
        booking_id = f"TRANSPORT-{uuid.uuid4().hex[:12].upper()}"

        booking_data = {
            "booking_id": booking_id,
            "type": BookingType.TRANSPORT,
            "option": option_data,
            "user": user_info,
            "passenger_name": option_data.get("passenger_name") or user_info.get("name"),
            "passenger_id": option_data.get("passenger_id") or user_info.get("id_number"),
            "created_at": datetime.now().isoformat()
        }

        booking = BookingStateMachine(booking_id, BookingType.TRANSPORT, booking_data)
        self._bookings[booking_id] = booking

        logger.info(f"Created transport booking: {booking_id}")
        return booking.to_dict()

    def create_hotel_booking(self, option_data: dict, user_info: dict, stay_dates: dict) -> dict:
        booking_id = f"HOTEL-{uuid.uuid4().hex[:12].upper()}"

        booking_data = {
            "booking_id": booking_id,
            "type": BookingType.HOTEL,
            "option": option_data,
            "user": user_info,
            "check_in": stay_dates.get("check_in"),
            "check_out": stay_dates.get("check_out"),
            "guest_name": option_data.get("guest_name") or user_info.get("name"),
            "created_at": datetime.now().isoformat()
        }

        booking = BookingStateMachine(booking_id, BookingType.HOTEL, booking_data)
        self._bookings[booking_id] = booking

        logger.info(f"Created hotel booking: {booking_id}")
        return booking.to_dict()

    def create_dining_booking(self, option_data: dict, user_info: dict, dining_info: dict) -> dict:
        booking_id = f"DINING-{uuid.uuid4().hex[:12].upper()}"

        booking_data = {
            "booking_id": booking_id,
            "type": BookingType.DINING,
            "option": option_data,
            "user": user_info,
            "date": dining_info.get("date"),
            "time": dining_info.get("time"),
            "headcount": dining_info.get("headcount"),
            "guest_name": user_info.get("name"),
            "created_at": datetime.now().isoformat()
        }

        booking = BookingStateMachine(booking_id, BookingType.DINING, booking_data)
        self._bookings[booking_id] = booking

        logger.info(f"Created dining booking: {booking_id}")
        return booking.to_dict()

    def confirm_booking(self, booking_id: str, confirmation_data: dict = None) -> dict:
        booking = self._bookings.get(booking_id)
        if not booking:
            return {"status": "error", "message": f"Booking {booking_id} not found"}

        if not booking.transition(BookingStatus.CONFIRMED, "User confirmed"):
            return {"status": "error", "message": f"Cannot confirm booking in status {booking.status}"}

        if confirmation_data:
            booking.data.update(confirmation_data)

        booking.data["confirmed_at"] = datetime.now().isoformat()
        booking.data["confirmation_number"] = f"CONF-{uuid.uuid4().hex[:8].upper()}"

        logger.info(f"Confirmed booking: {booking_id}")
        return booking.to_dict()

    def cancel_booking(self, booking_id: str, reason: str = None) -> dict:
        booking = self._bookings.get(booking_id)
        if not booking:
            return {"status": "error", "message": f"Booking {booking_id} not found"}

        if not booking.transition(BookingStatus.CANCELLED, reason or "User cancelled"):
            return {"status": "error", "message": f"Cannot cancel booking in status {booking.status}"}

        booking.data["cancelled_at"] = datetime.now().isoformat()
        booking.data["cancellation_reason"] = reason

        logger.info(f"Cancelled booking: {booking_id}")
        return booking.to_dict()

    def complete_booking(self, booking_id: str, completion_data: dict = None) -> dict:
        booking = self._bookings.get(booking_id)
        if not booking:
            return {"status": "error", "message": f"Booking {booking_id} not found"}

        if not booking.transition(BookingStatus.COMPLETED, "Service rendered"):
            return {"status": "error", "message": f"Cannot complete booking in status {booking.status}"}

        if completion_data:
            booking.data.update(completion_data)

        booking.data["completed_at"] = datetime.now().isoformat()

        logger.info(f"Completed booking: {booking_id}")
        return booking.to_dict()

    def fail_booking(self, booking_id: str, error: str) -> dict:
        booking = self._bookings.get(booking_id)
        if not booking:
            return {"status": "error", "message": f"Booking {booking_id} not found"}

        if not booking.transition(BookingStatus.FAILED, error):
            return {"status": "error", "message": f"Cannot fail booking in status {booking.status}"}

        booking.data["failed_at"] = datetime.now().isoformat()
        booking.data["error"] = error

        logger.error(f"Booking failed: {booking_id} - {error}")
        return booking.to_dict()

    def get_booking(self, booking_id: str) -> Optional[dict]:
        booking = self._bookings.get(booking_id)
        if booking:
            return booking.to_dict()
        return None

    def list_bookings(
        self,
        status: BookingStatus = None,
        booking_type: BookingType = None,
        user_id: str = None
    ) -> List[dict]:
        results = []
        for booking in self._bookings.values():
            if status and booking.status != status:
                continue
            if booking_type and booking.booking_type != booking_type:
                continue
            if user_id and booking.data.get("user", {}).get("user_id") != user_id:
                continue
            results.append(booking.to_dict())
        return results

    def retry_booking(self, booking_id: str) -> dict:
        booking = self._bookings.get(booking_id)
        if not booking:
            return {"status": "error", "message": f"Booking {booking_id} not found"}

        if booking.status != BookingStatus.FAILED:
            return {"status": "error", "message": f"Can only retry failed bookings"}

        if not booking.transition(BookingStatus.PENDING, "Retrying booking"):
            return {"status": "error", "message": f"Cannot retry booking"}

        booking.data["retried_at"] = datetime.now().isoformat()

        logger.info(f"Retrying booking: {booking_id}")
        return booking.to_dict()


booking_service = BookingService()
