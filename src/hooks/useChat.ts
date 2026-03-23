import { useState, useCallback, useRef } from "react";
import { apiClient } from "@/lib/api";
import type {
  ChatMessage,
  ChatRequest,
  TransportSearchResponse,
  HotelSearchResponse,
  DiningSearchResponse,
  BookingResponse,
} from "@/lib/api-types";

export interface UseChatOptions {
  sessionId?: string;
  onError?: (error: Error) => void;
  onAgentResponse?: (agentId: string, message: string, missingFields?: string[], questions?: any[]) => void;
  onMessage?: (message: ChatMessage) => void;
  onStreamingUpdate?: (content: string) => void;
  onIntentUpdate?: (data: { missingFields: string[]; questions: any[]; isComplete: boolean }) => void;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  streamingContent: string | null;
  isLoading: boolean;
  sessionId: string | null;
  missingFields: string[];
  questions: any[];
  isIntentComplete: boolean;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  searchTransport: (request: any) => Promise<TransportSearchResponse | null>;
  searchHotel: (request: any) => Promise<HotelSearchResponse | null>;
  searchDining: (request: any) => Promise<DiningSearchResponse | null>;
  createBooking: (type: string, data: any) => Promise<BookingResponse | null>;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingContent, setStreamingContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(options.sessionId || null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [questions, setQuestions] = useState<any[]>([]);
  const [isIntentComplete, setIsIntentComplete] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const fullContentRef = useRef<string>("");
  const assistantMessageIdRef = useRef<string | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    const currentAssistantMsgId = assistantMessageIdRef.current;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    fullContentRef.current = "";
    assistantMessageIdRef.current = null;

    setMessages((prev) => {
      const filtered = prev.filter((msg) => msg.id !== currentAssistantMsgId);
      return filtered;
    });
    setStreamingContent("");
    setMissingFields([]);
    setQuestions([]);
    setIsIntentComplete(false);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const request: ChatRequest = {
        message,
        session_id: sessionId || undefined,
      };

      const controller = new AbortController();
      abortControllerRef.current = controller;

      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (options.onStreamingUpdate) {
        options.onStreamingUpdate("");
      }

      let buffer = "";
      let messageCreated = false;

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            try {
              const jsonStr = line.slice(5).trim();
              if (!jsonStr) continue;

              const data = JSON.parse(jsonStr);
              
              if (data.content) {
                fullContentRef.current += data.content;
                setStreamingContent(fullContentRef.current);

                if (!messageCreated) {
                  assistantMessageIdRef.current = `assistant-${Date.now()}`;
                  const assistantMessage: ChatMessage = {
                    id: assistantMessageIdRef.current,
                    role: "assistant",
                    content: fullContentRef.current,
                    agentId: "intent",
                    timestamp: new Date(),
                  };
                  setMessages((prev) => [...prev, assistantMessage]);
                  messageCreated = true;
                } else {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageIdRef.current
                        ? { ...msg, content: fullContentRef.current }
                        : msg
                    )
                  );
                }

                if (options.onStreamingUpdate) {
                  options.onStreamingUpdate(fullContentRef.current);
                }
              }

              if (data.type === "end" || data.missing_fields || data.questions) {
                const newMissingFields = data.missing_fields || [];
                const newQuestions = data.questions || [];
                const newIsComplete = data.is_complete || false;

                if (newMissingFields.length > 0 || newQuestions.length > 0) {
                  setMissingFields(newMissingFields);
                  setQuestions(newQuestions);
                  setIsIntentComplete(newIsComplete);

                  if (options.onIntentUpdate) {
                    options.onIntentUpdate({
                      missingFields: newMissingFields,
                      questions: newQuestions,
                      isComplete: newIsComplete
                    });
                  }
                }
              }
            } catch (e) {
              console.error("Parse error:", e);
            }
          }
        }
      }

      if (options.onAgentResponse) {
        options.onAgentResponse("intent", fullContentRef.current, missingFields, questions);
      }

      setStreamingContent(null);
      abortControllerRef.current = null;

    } catch (error: any) {
      if (error.name === "AbortError") {
        setStreamingContent(null);
        return;
      }

      console.error("Chat error:", error);

      setMessages((prev) =>
        prev.filter((msg) => msg.id !== assistantMessageIdRef.current)
      );

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "抱歉，服务暂时不可用，请稍后再试。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      if (options.onMessage) {
        options.onMessage(errorMessage);
      }

      if (options.onError && error instanceof Error) {
        options.onError(error);
      }

      setStreamingContent(null);
      abortControllerRef.current = null;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, options]);

  const clearMessages = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    fullContentRef.current = "";
    setMessages([]);
    setStreamingContent(null);
    setSessionId(null);
    setMissingFields([]);
    setQuestions([]);
    setIsIntentComplete(false);
  }, []);

  const searchTransport = useCallback(async (request: any) => {
    try {
      const response = await apiClient.asyncTransportSearch(request);
      if (response.code === 0) {
        return response.data;
      }
    } catch (error) {
      console.error("Transport search error:", error);
    }
    return null;
  }, []);

  const searchHotel = useCallback(async (request: any) => {
    try {
      const response = await apiClient.asyncHotelSearch(request);
      if (response.code === 0) {
        return response.data;
      }
    } catch (error) {
      console.error("Hotel search error:", error);
    }
    return null;
  }, []);

  const searchDining = useCallback(async (request: any) => {
    try {
      const response = await apiClient.asyncDiningSearch(request);
      if (response.code === 0) {
        return response.data;
      }
    } catch (error) {
      console.error("Dining search error:", error);
    }
    return null;
  }, []);

  const createBooking = useCallback(async (type: string, data: any) => {
    try {
      let response;
      switch (type) {
        case "transport":
          response = await apiClient.asyncCreateTransportBooking(data);
          break;
        case "hotel":
          response = await apiClient.asyncCreateHotelBooking(data);
          break;
        case "dining":
          response = await apiClient.asyncCreateDiningBooking(data);
          break;
        default:
          return null;
      }
      if (response.code === 0) {
        return response.data;
      }
    } catch (error) {
      console.error("Booking error:", error);
    }
    return null;
  }, []);

  return {
    messages,
    streamingContent,
    isLoading,
    sessionId,
    missingFields,
    questions,
    isIntentComplete,
    sendMessage,
    clearMessages,
    searchTransport,
    searchHotel,
    searchDining,
    createBooking,
  };
}

export default useChat;
