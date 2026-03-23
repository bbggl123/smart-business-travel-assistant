import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Send, Mic, Paperclip, ArrowLeft, Menu, X, ChevronRight, Wifi, WifiOff } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { agents, ChatMessage, type Conversation } from "@/lib/mock-data";
import { MessageCardRenderer } from "@/components/chat/MessageCard";
import { AgentTag } from "@/components/chat/AgentTag";
import { useIsMobile } from "@/hooks/use-mobile";
import { useChat } from "@/hooks/useChat";
import avatarHead from "@/assets/avatar-head.png";
import { apiClient } from "@/lib/api";

const INITIAL_MESSAGE: ChatMessage = {
  id: "init",
  role: "assistant",
  content: "您好！我是智能商旅助手。请问有什么可以帮您？",
  timestamp: new Date(),
};

export default function ChatPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useIsMobile();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [input, setInput] = useState((location.state as any)?.initialMessage || "");
  const [activeAgent, setActiveAgent] = useState("smart");
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [conversations] = useState<Conversation[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionChecked, setConnectionChecked] = useState(false);

  const { messages: chatMessages, streamingContent, sendMessage, isLoading } = useChat({
    sessionId: (location.state as any)?.sessionId,
    onError: (error) => {
      console.error("Chat error:", error);
    },
  });

  const messages = chatMessages.length > 0 ? chatMessages : [INITIAL_MESSAGE];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  useEffect(() => {
    apiClient.asyncHealthCheck()
      .then((res) => {
        if (res && res.status === "healthy") {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
        setConnectionChecked(true);
      })
      .catch((err) => {
        console.error("Health check failed:", err);
        setIsConnected(false);
        setConnectionChecked(true);
      });
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const currentInput = input;
    setInput("");

    try {
      await sendMessage(currentInput);
    } catch (error) {
      console.error("Send message error:", error);
    }
  };

  const currentAgent = agents.find((a) => a.id === activeAgent);

  return (
    <div className="h-screen flex bg-background overflow-hidden">
      <aside
        className={`${
          isMobile
            ? `fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ${
                sidebarOpen ? "translate-x-0" : "-translate-x-full"
              }`
            : `w-72 shrink-0 border-r transition-all duration-300 ${
                sidebarOpen ? "translate-x-0" : "-translate-x-full w-0 border-0"
              }`
        } bg-card flex flex-col`}
      >
        <div className="p-4 flex items-center justify-between border-b">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-sm">对话历史</h2>
          </div>
          <div className="flex items-center gap-2">
            {connectionChecked ? (
              isConnected ? (
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-green-50 border border-green-200">
                  <Wifi className="w-3.5 h-3.5 text-green-600" />
                  <span className="text-xs font-medium text-green-700">后端已连接</span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-50 border border-red-200">
                  <WifiOff className="w-3.5 h-3.5 text-red-600" />
                  <span className="text-xs font-medium text-red-700">后端离线</span>
                </div>
              )
            ) : (
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-gray-50 border border-gray-200">
                <div className="w-3 h-3 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs text-gray-500">检测中...</span>
              </div>
            )}
          </div>
          {isMobile && (
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1 rounded hover:bg-muted"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className="w-full text-left p-3 rounded-lg hover:bg-accent transition-colors group"
            >
              <div className="text-sm font-medium truncate">{conv.title}</div>
              <div className="text-xs text-muted-foreground truncate mt-0.5">
                {conv.lastMessage}
              </div>
              <div className="flex gap-1 mt-1.5 flex-wrap">
                {conv.agentIds.slice(0, 3).map((id) => {
                  const ag = agents.find((a) => a.id === id);
                  if (!ag) return null;
                  const Icon = ag.icon;
                  return <Icon key={id} className="w-3 h-3 text-primary/60" />;
                })}
                {conv.agentIds.length > 3 && (
                  <span className="text-[10px] text-muted-foreground">
                    +{conv.agentIds.length - 3}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="border-t p-3">
          <p className="text-xs text-muted-foreground mb-2 font-medium">
            选择Agent
          </p>
          <div className="space-y-0.5 max-h-48 overflow-y-auto">
            {agents.map((agent) => {
              const Icon = agent.icon;
              const isActive = activeAgent === agent.id;
              return (
                <button
                  key={agent.id}
                  onClick={() => setActiveAgent(agent.id)}
                  className={`w-full flex items-center gap-2.5 p-2 rounded-lg text-left text-sm transition-all active:scale-[0.97] ${
                    isActive
                      ? "bg-primary/10 text-primary font-medium"
                      : "hover:bg-muted"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 shrink-0 ${
                      isActive ? "text-primary" : "text-muted-foreground"
                    }`}
                  />
                  <div className="min-w-0">
                    <div className="truncate">{agent.name}</div>
                    <div className="text-[10px] text-muted-foreground truncate">
                      {agent.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </aside>

      {isMobile && sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center gap-3 px-4 py-3 border-b bg-card/80 backdrop-blur-sm shrink-0">
          <button
            onClick={() => (isMobile ? setSidebarOpen(true) : setSidebarOpen((p) => !p))}
            className="p-2 rounded-lg hover:bg-muted transition-colors active:scale-95"
          >
            <Menu className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate("/")}
            className="p-2 rounded-lg hover:bg-muted transition-colors active:scale-95"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              {currentAgent && <currentAgent.icon className="w-3.5 h-3.5 text-primary" />}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate">
                {currentAgent?.name || "智能协作"}
              </div>
            </div>
          </div>

          {isMobile && (
            <div className="flex gap-1 overflow-x-auto no-scrollbar">
              {agents.slice(0, 4).map((a) => {
                const Icon = a.icon;
                return (
                  <button
                    key={a.id}
                    onClick={() => setActiveAgent(a.id)}
                    className={`shrink-0 p-1.5 rounded-lg ${
                      activeAgent === a.id ? "bg-primary/10" : ""
                    }`}
                  >
                    <Icon
                      className={`w-4 h-4 ${
                        activeAgent === a.id ? "text-primary" : "text-muted-foreground"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          )}

          <button
            onClick={() => navigate("/live")}
            className="shrink-0 p-2 rounded-lg hover:bg-muted transition-colors active:scale-95"
          >
            <Mic className="w-4 h-4 text-primary" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              } opacity-0 animate-fade-in`}
              style={{ animationDelay: `${Math.min(idx * 0.05, 0.5)}s` }}
            >
              {msg.role === "assistant" && (
                <img
                  src={avatarHead}
                  alt=""
                  className="w-8 h-8 rounded-full shrink-0 mt-1 ring-2 ring-primary/10"
                />
              )}
              <div className={`max-w-[80%] md:max-w-[65%] ${msg.role === "user" ? "order-first" : ""}`}>
                {msg.agentId && (
                  <div className="mb-1">
                    <AgentTag agentId={msg.agentId} />
                  </div>
                )}
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-md"
                      : "bg-card border rounded-bl-md shadow-sm"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                      {streamingContent !== null && msg.id === messages[messages.length - 1]?.id && (
                        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
                      )}
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
                {msg.card && <MessageCardRenderer card={msg.card} />}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t bg-card/80 backdrop-blur-sm p-3 shrink-0">
          <form onSubmit={handleSend} className="flex items-center gap-2 max-w-3xl mx-auto">
            <button
              type="button"
              className="p-2.5 rounded-xl hover:bg-muted transition-colors active:scale-95"
            >
              <Paperclip className="w-4 h-4 text-muted-foreground" />
            </button>
            <div className="flex-1 flex items-center border rounded-2xl bg-background px-4 py-2.5 focus-within:ring-2 focus-within:ring-primary/20 transition-shadow">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={!connectionChecked ? "正在连接后端..." : isConnected ? "输入消息..." : "后端离线，请检查服务"}
                disabled={!isConnected || isLoading}
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:opacity-50"
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || !isConnected || isLoading}
              className="p-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-all active:scale-95"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
