import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { MessageSquare, MicOff, Mic, PhoneOff, ChevronRight, ChevronLeft } from "lucide-react";
import { AgentTag } from "@/components/chat/AgentTag";
import { apiClient } from "@/lib/api";
import avatarFull from "@/assets/avatar-full.png";

interface TranscriptMessage {
  role: "user" | "assistant";
  text: string;
  timestamp: Date;
}

function WaveformBar({ delay }: { delay: number }) {
  return (
    <div
      className="w-1 rounded-full bg-primary/70"
      style={{
        animation: `waveform 0.8s ease-in-out infinite`,
        animationDelay: `${delay}s`,
        height: "8px",
      }}
    />
  );
}

export default function LiveTalkingPage() {
  const navigate = useNavigate();
  const [isMuted, setIsMuted] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcriptOpen, setTranscriptOpen] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [transcriptMessages, setTranscriptMessages] = useState<TranscriptMessage[]>([
    {
      role: "assistant",
      text: "您好，我是智能商旅助手。请问有什么可以帮您？",
      timestamp: new Date(),
    },
  ]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    apiClient.asyncHealthCheck()
      .then((res) => {
        if (res && res.status === "healthy") {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      })
      .catch(() => setIsConnected(false));
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        await processAudio(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsListening(true);
      setCurrentTranscript("正在聆听...");
    } catch (error) {
      console.error("Failed to start recording:", error);
      setIsListening(false);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      setIsListening(false);
    }
  }, [isListening]);

  const processAudio = async (audioBlob: Blob) => {
    try {
      const file = new File([audioBlob], "audio.webm", { type: "audio/webm" });

      setCurrentTranscript("识别中...");

      const asrResponse = await apiClient.asyncASR(file, "zh");

      if (asrResponse.code === 0 && asrResponse.data) {
        const userText = asrResponse.data.text;

        setTranscriptMessages((prev) => [
          ...prev,
          { role: "user", text: userText, timestamp: new Date() },
        ]);
        setCurrentTranscript("");

        const chatResponse = await apiClient.asyncChat({
          message: userText,
          session_id: `voice_${Date.now()}`,
        });

        if (chatResponse.code === 0 && chatResponse.data) {
          const assistantText = chatResponse.data.message;

          setTranscriptMessages((prev) => [
            ...prev,
            { role: "assistant", text: assistantText, timestamp: new Date() },
          ]);

          await playTTS(assistantText);
        }
      }
    } catch (error) {
      console.error("Process audio error:", error);
      setCurrentTranscript("");
    }
  };

  const playTTS = async (text: string) => {
    try {
      setIsSpeaking(true);

      const response = await apiClient.asyncTTS({
        text,
        voice: "female_yiyi",
        speed: 1.0,
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        audioRef.current = new Audio(audioUrl);

        audioRef.current.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
        };

        audioRef.current.onerror = () => {
          setIsSpeaking(false);
        };

        await audioRef.current.play();
      } else {
        setIsSpeaking(false);
      }
    } catch (error) {
      console.error("TTS error:", error);
      setIsSpeaking(false);
    }
  };

  const toggleMic = useCallback(() => {
    if (isListening) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isListening, startRecording, stopRecording]);

  const handleEndCall = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    navigate("/");
  }, [navigate]);

  return (
    <div className="h-screen flex flex-col bg-foreground/[0.03] relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] rounded-full bg-primary/5 blur-[100px]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-primary/3 blur-[80px]" />
      </div>

      <header className="relative z-10 flex items-center justify-between px-4 py-3">
        <button
          onClick={() => navigate("/chat")}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-card/80 backdrop-blur-sm border text-sm hover:bg-card transition-colors active:scale-[0.97]"
        >
          <MessageSquare className="w-4 h-4 text-primary" />
          <span className="hidden sm:inline">返回文字模式</span>
        </button>

        <div className="flex items-center gap-2">
          <span
            className={`text-xs px-2 py-1 rounded ${
              isConnected
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {isConnected ? "在线" : "离线"}
          </span>
        </div>

        <button
          onClick={() => setTranscriptOpen((p) => !p)}
          className="p-2 rounded-xl bg-card/80 backdrop-blur-sm border hover:bg-card transition-colors active:scale-[0.97]"
        >
          {transcriptOpen ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </header>

      <div className="relative z-10 flex-1 flex">
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="relative">
            {(isListening || isSpeaking) && (
              <>
                <div className="absolute inset-[-20px] rounded-full border-2 border-primary/20 animate-pulse-ring" />
                <div
                  className="absolute inset-[-40px] rounded-full border border-primary/10 animate-pulse-ring"
                  style={{ animationDelay: "0.5s" }}
                />
              </>
            )}
            <img
              src={avatarFull}
              alt="数字人助手"
              className={`w-64 h-64 md:w-80 md:h-80 object-contain drop-shadow-2xl transition-all duration-500 ${
                isListening || isSpeaking ? "scale-105" : "animate-breathe"
              }`}
            />
          </div>

          <div className="mt-6 text-center">
            <p
              className={`text-sm font-medium ${
                isListening || isSpeaking ? "text-primary" : "text-muted-foreground"
              }`}
            >
              {isSpeaking
                ? "正在回复..."
                : isListening
                ? "正在聆听..."
                : "点击麦克风开始对话"}
            </p>
            {currentTranscript && (isListening || isSpeaking) && (
              <p className="mt-2 text-base text-foreground/80 animate-fade-in max-w-sm">
                {currentTranscript}
              </p>
            )}
          </div>

          <div className="flex items-center gap-1 mt-6 h-8">
            {(isListening || isSpeaking) && (
              <>
                {Array.from({ length: isSpeaking ? 12 : 24 }).map((_, i) => (
                  <WaveformBar key={i} delay={i * 0.05} />
                ))}
              </>
            )}
          </div>
        </div>

        {transcriptOpen && (
          <aside
            className="w-80 bg-card/90 backdrop-blur-sm border-l flex flex-col animate-fade-in-right"
            style={{ animationDuration: "0.3s" }}
          >
            <div className="p-4 border-b">
              <h3 className="font-semibold text-sm">对话记录</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {transcriptMessages.map((msg, i) => (
                <div key={i} className={`text-sm ${msg.role === "user" ? "text-right" : ""}`}>
                  <span
                    className={`inline-block px-3 py-2 rounded-xl max-w-[90%] ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {msg.text}
                  </span>
                </div>
              ))}
            </div>
          </aside>
        )}
      </div>

      <div className="relative z-10 flex items-center justify-center gap-6 pb-8 pt-4">
        <button
          onClick={toggleMic}
          disabled={!isConnected || isSpeaking}
          className={`p-5 rounded-full transition-all duration-300 active:scale-90 ${
            isListening
              ? "bg-primary text-primary-foreground shadow-lg shadow-primary/30 scale-110"
              : isConnected
              ? "bg-card border shadow-md hover:shadow-lg"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          }`}
        >
          {isListening ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
        </button>
        <button
          onClick={handleEndCall}
          className="p-4 rounded-full bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors active:scale-90"
        >
          <PhoneOff className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
