from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: Optional[str] = None
    level: str = "基层员工"
    department: Optional[str] = None
    created_at: Optional[datetime] = None


class Session(BaseModel):
    id: Optional[str] = None
    user_id: str
    status: str = "active"
    context: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Message(BaseModel):
    id: Optional[str] = None
    session_id: str
    role: str
    content: str
    agent_id: Optional[str] = None
    card_type: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class TripPlan(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    purpose: Optional[str] = None
    departure: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    headcount: int = 1
    user_level: str = "基层员工"
    status: str = "planning"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TransportOption(BaseModel):
    id: Optional[str] = None
    trip_id: str
    type: str
    provider: str
    flight_no: Optional[str] = None
    departure_city: str
    departure_code: str
    departure_time: str
    arrival_city: str
    arrival_code: str
    arrival_time: str
    duration: str
    price: float
    is_selected: bool = False
    booking_id: Optional[str] = None
    created_at: Optional[datetime] = None


class HotelOption(BaseModel):
    id: Optional[str] = None
    trip_id: str
    name: str
    stars: int
    city: str
    district: Optional[str] = None
    address: Optional[str] = None
    price: float
    distance_km: Optional[float] = None
    facilities: List[str] = Field(default_factory=list)
    is_selected: bool = False
    booking_id: Optional[str] = None
    created_at: Optional[datetime] = None


class DiningOption(BaseModel):
    id: Optional[str] = None
    trip_id: str
    restaurant: str
    cuisine: str
    city: str
    address: Optional[str] = None
    price_per_person: float
    headcount: int
    total_amount: float
    has_private_room: bool = False
    recommended_dishes: List[dict] = Field(default_factory=list)
    is_selected: bool = False
    booking_id: Optional[str] = None
    created_at: Optional[datetime] = None


class Booking(BaseModel):
    id: Optional[str] = None
    trip_id: str
    user_id: str
    type: str
    status: str = "pending"
    details: dict = Field(default_factory=dict)
    total_amount: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApprovalForm(BaseModel):
    id: Optional[str] = None
    trip_id: str
    user_id: str
    employee_name: str
    employee_level: str
    department: str
    purpose: str
    departure: str
    destination: str
    start_date: str
    end_date: str
    items: List[dict] = Field(default_factory=list)
    total_amount: float = 0.0
    status: str = "draft"
    pdf_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Invoice(BaseModel):
    id: Optional[str] = None
    user_id: str
    invoice_code: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    total_amount: Optional[float] = None
    tax_rate: Optional[float] = None
    invoice_type: str = "normal"
    status: str = "pending"
    confidence: dict = Field(default_factory=dict)
    low_confidence_fields: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
