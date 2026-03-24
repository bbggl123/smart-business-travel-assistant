import type {
  ApiResponse,
  ChatRequest,
  ChatResponse,
  TransportSearchRequest,
  TransportSearchResponse,
  HotelSearchRequest,
  HotelSearchResponse,
  DiningSearchRequest,
  DiningSearchResponse,
  ComplianceCheckRequest,
  ComplianceCheckResponse,
  ApprovalGenerateRequest,
  ApprovalGenerateResponse,
  InvoiceRecognizeRequest,
  InvoiceRecognizeResponse,
  BookingCreateRequest,
  BookingResponse,
  TTSRequest,
  ASRResponse,
  VoiceConversationRequest,
} from "./api-types";

const API_BASE_URL = "";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders: HeadersInit = {
      "Content-Type": "application/json",
    };

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data as T;
  }

  asyncChat(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    return this.request<ApiResponse<ChatResponse>>("/api/chat/send", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncChatStream(
    request: ChatRequest,
    onChunk: (content: string) => void,
    onComplete: (fullContent: string) => void,
    onError: (error: Error) => void
  ): () => void {
    const url = `${this.baseUrl}/api/chat/stream`;

    const eventSource = new EventSource(`/api/chat/stream?${new URLSearchParams({
      message: request.message,
      session_id: request.session_id || ""
    })}`);

    let fullContent = "";

    eventSource.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.content) {
          fullContent += data.content;
          onChunk(fullContent);
        }
      } catch (e) {
        console.error("Parse error:", e);
      }
    });

    eventSource.addEventListener("message_end", (event) => {
      try {
        const data = JSON.parse(event.data);
        onComplete(data.content || fullContent);
      } catch (e) {
        onComplete(fullContent);
      }
      eventSource.close();
    });

    eventSource.addEventListener("error", (event) => {
      eventSource.close();
      onError(new Error("Stream connection error"));
    });

    return () => {
      eventSource.close();
    };
  }

  asyncChatStreamPOST(
    request: ChatRequest,
    onChunk: (content: string) => void,
    onComplete: (fullContent: string) => void,
    onError: (error: Error) => void
  ): () => void {
    const url = `${this.baseUrl}/api/chat/stream`;

    const controller = new AbortController();
    let fullContent = "";
    let parsed = false;

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        function read() {
          reader?.read().then(({ done, value }) => {
            if (done) {
              if (!parsed) {
                onComplete(fullContent);
              }
              return;
            }

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
              if (line.startsWith("data:")) {
                try {
                  const data = JSON.parse(line.slice(5));
                  if (data.content) {
                    fullContent += data.content;
                    onChunk(fullContent);
                    parsed = true;
                  }
                  if (data.type === "end" && data.content) {
                    fullContent = data.content;
                    parsed = true;
                  }
                } catch (e) {
                }
              }
            }

            read();
          });
        }

        read();
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          onError(error);
        }
      });

    return () => {
      controller.abort();
    };
  }

  asyncTransportSearch(
    request: TransportSearchRequest
  ): Promise<ApiResponse<TransportSearchResponse>> {
    return this.request<ApiResponse<TransportSearchResponse>>(
      "/api/transport/search",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  asyncHotelSearch(
    request: HotelSearchRequest
  ): Promise<ApiResponse<HotelSearchResponse>> {
    return this.request<ApiResponse<HotelSearchResponse>>("/api/hotel/search", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncDiningSearch(
    request: DiningSearchRequest
  ): Promise<ApiResponse<DiningSearchResponse>> {
    return this.request<ApiResponse<DiningSearchResponse>>("/api/dining/search", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncComplianceCheck(
    request: ComplianceCheckRequest
  ): Promise<ApiResponse<ComplianceCheckResponse>> {
    return this.request<ApiResponse<ComplianceCheckResponse>>(
      "/api/compliance/check",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  asyncApprovalGenerate(
    request: ApprovalGenerateRequest
  ): Promise<ApiResponse<ApprovalGenerateResponse>> {
    return this.request<ApiResponse<ApprovalGenerateResponse>>(
      "/api/approval/generate",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  asyncSelectionConfirm(
    sessionId: string,
    tripData: any,
    transportSelection: any,
    hotelSelection: any,
    diningSelection: any
  ): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>(
      "/api/chat/selection/confirm",
      {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          trip_data: tripData,
          transport_selection: transportSelection,
          hotel_selection: hotelSelection,
          dining_selection: diningSelection,
        }),
      }
    );
  }

  asyncInvoiceRecognize(
    request: InvoiceRecognizeRequest
  ): Promise<ApiResponse<InvoiceRecognizeResponse>> {
    return this.request<ApiResponse<InvoiceRecognizeResponse>>(
      "/api/invoice/recognize",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  asyncCreateTransportBooking(
    request: BookingCreateRequest
  ): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>("/booking/transport", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncCreateHotelBooking(
    request: BookingCreateRequest & { stay_dates: any }
  ): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>("/booking/hotel", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncCreateDiningBooking(
    request: BookingCreateRequest & { dining_info: any }
  ): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>("/booking/dining", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  asyncConfirmBooking(bookingId: string): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>(
      `/booking/${bookingId}/confirm`,
      {
        method: "POST",
      }
    );
  }

  asyncCancelBooking(
    bookingId: string,
    reason?: string
  ): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>(
      `/booking/${bookingId}/cancel`,
      {
        method: "POST",
        body: reason ? JSON.stringify({ reason }) : undefined,
      }
    );
  }

  asyncGetBooking(bookingId: string): Promise<ApiResponse<BookingResponse>> {
    return this.request<ApiResponse<BookingResponse>>(`/booking/${bookingId}`);
  }

  asyncListBookings(
    status?: string,
    bookingType?: string
  ): Promise<ApiResponse<{ bookings: BookingResponse[]; count: number }>> {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (bookingType) params.append("booking_type", bookingType);
    const query = params.toString();
    return this.request<ApiResponse<{ bookings: BookingResponse[]; count: number }>>(
      `/booking/${query ? `?${query}` : ""}`
    );
  }

  asyncTTS(request: TTSRequest): Promise<Response> {
    const formData = new FormData();
    formData.append("text", request.text);
    if (request.voice) formData.append("voice", request.voice);
    if (request.speed) formData.append("speed", request.speed.toString());

    return fetch(`${this.baseUrl}/voice/tts`, {
      method: "POST",
      body: formData,
    });
  }

  asyncASR(file: File, language?: string): Promise<ApiResponse<ASRResponse>> {
    const formData = new FormData();
    formData.append("audio", file);
    if (language) formData.append("language", language);

    return this.request<ApiResponse<ASRResponse>>("/voice/asr", {
      method: "POST",
      headers: {},
      body: formData,
    });
  }

  asyncVoiceConversation(
    request: VoiceConversationRequest
  ): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append("audio", request.audio);
    if (request.session_id) formData.append("session_id", request.session_id);

    return this.request<ApiResponse<any>>("/voice/conversation", {
      method: "POST",
      headers: {},
      body: formData,
    });
  }

  asyncGetVoices(): Promise<ApiResponse<{ voices: any[] }>> {
    return this.request<ApiResponse<{ voices: any[] }>>("/voice/voices");
  }

  asyncGetASRInfo(): Promise<ApiResponse<any>> {
    return this.request<ApiResponse<any>>("/voice/asr/info");
  }

  asyncHealthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  asyncSimpleHealthCheck(): Promise<{ connected: boolean }> {
    return this.request<{ connected: boolean }>("/health");
  }
}

export const apiClient = new ApiClient();
export default apiClient;
