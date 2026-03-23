export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  agent_id?: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  agent_id?: string;
  intent_type?: string;
  workflow_id?: string;
}

export interface TransportSearchRequest {
  departure: string;
  destination: string;
  date: string;
  type?: "flight" | "train" | "both";
  user_level?: string;
}

export interface TransportOption {
  id: string;
  type: "flight" | "train";
  provider: string;
  flight_no?: string;
  train_no?: string;
  departure: { city: string; code: string; time: string };
  arrival: { city: string; code: string; time: string };
  duration: string;
  price: number;
}

export interface TransportSearchResponse {
  status: string;
  recommendations: Array<{
    category: "recommended" | "alternative";
    type: "flight" | "train";
    option: TransportOption;
    compliance: {
      is_compliant: boolean;
      limit: number;
      over_budget?: number;
      savings?: number;
    };
    reason: string;
  }>;
  total_options: number;
  flight_policy?: any;
  train_policy?: any;
}

export interface HotelSearchRequest {
  city: string;
  check_in: string;
  check_out: string;
  star?: number;
  user_level?: string;
  customer_location?: string;
}

export interface HotelOption {
  id: string;
  name: string;
  stars: number;
  price: number;
  district: string;
  address: string;
  distance_km: number;
  distance_info: string;
  transport_info: string;
  facilities: string[];
  compliance: {
    is_compliant: boolean;
    limit: number;
    over_budget?: number;
  };
}

export interface HotelSearchResponse {
  status: string;
  compliant_hotels: HotelOption[];
  alternative_hotels: HotelOption[];
  total_compliant: number;
  total_alternative: number;
  budget_limit: number;
  city_tier: string;
  used_real_distance: boolean;
}

export interface DiningSearchRequest {
  city: string;
  date?: string;
  headcount: number;
  cuisine?: string;
  budget_per_person?: number;
}

export interface RestaurantOption {
  id: string;
  restaurant: string;
  cuisine: string;
  city: string;
  address: string;
  price_per_person: number;
  headcount: number;
  total_amount: number;
  has_private_room: boolean;
  suggested_dishes: Array<{
    name: string;
    price: number;
    suitable_for: number;
  }>;
  dishes_total_price: number;
  compliance: {
    is_compliant: boolean;
    limit: number;
    over_budget?: number;
  };
}

export interface DiningSearchResponse {
  status: string;
  is_over_budget: boolean;
  compliant_restaurants: RestaurantOption[];
  over_budget_restaurants: RestaurantOption[];
  total_compliant: number;
  total_over_budget: number;
  dining_limit: number;
  city_tier: string;
}

export interface ComplianceCheckRequest {
  category: "transport" | "hotel" | "dining";
  user_level: string;
  city?: string;
  amount: number;
}

export interface ComplianceCheckResponse {
  is_compliant: boolean;
  category: string;
  user_level: string;
  amount: number;
  limit: number;
  over_budget?: number;
  message: string;
}

export interface ApprovalGenerateRequest {
  session_id: string;
  user_info: {
    name: string;
    level: string;
    department?: string;
  };
  trip_data: {
    departure: string;
    destination: string;
    start_date: string;
    end_date: string;
    purpose: string;
  };
  transport_data?: any;
  hotel_data?: any;
  dining_data?: any;
}

export interface ApprovalGenerateResponse {
  status: string;
  approval_id: string;
  pdf_url?: string;
  html_content?: string;
  summary: {
    total_amount: number;
    items: Array<{ name: string; amount: number }>;
  };
}

export interface InvoiceRecognizeRequest {
  file_data?: string;
  file_type?: string;
  action?: string;
}

export interface InvoiceData {
  invoice_code?: string;
  invoice_number?: string;
  invoice_date?: string;
  buyer_name?: string;
  seller_name?: string;
  amount?: number;
  tax_amount?: number;
  total_amount?: number;
  tax_rate?: string;
  invoice_type?: string;
  items?: Array<{
    name: string;
    quantity: number;
    unit_price: number;
    amount: number;
  }>;
}

export interface InvoiceRecognizeResponse {
  status: string;
  invoice_data: InvoiceData;
  confidence: number;
  low_confidence_fields: string[];
  needs_review: boolean;
  message: string;
}

export interface BookingCreateRequest {
  option_data: any;
  user_info: any;
}

export interface BookingResponse {
  booking_id: string;
  booking_type: string;
  status: string;
  data: any;
  history: Array<{
    status: string;
    timestamp: string;
    event: string;
    reason?: string;
    from_status?: string;
  }>;
}

export interface TTSRequest {
  text: string;
  voice?: string;
  speed?: number;
}

export interface ASRRequest {
  audio?: File;
  language?: string;
}

export interface ASRResponse {
  text: string;
  language: string;
  duration: number;
}

export interface VoiceConversationRequest {
  audio: File;
  session_id?: string;
}

export interface COTResult {
  request_id: string;
  agent_name: string;
  is_complete: boolean;
  layers: Array<{
    layer_name: string;
    reasoning_steps: string[];
    confidence: number;
  }>;
}
