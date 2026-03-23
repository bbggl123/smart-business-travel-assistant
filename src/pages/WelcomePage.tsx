import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageSquare, Mic, CalendarRange, Hotel, UtensilsCrossed, Receipt, Send, Sparkles } from "lucide-react";
import avatarFull from "@/assets/avatar-full.png";

const quickActions = [
  { icon: CalendarRange, label: "行程规划", desc: "智能安排出差日程", color: "from-primary/10 to-primary/5" },
  { icon: Hotel, label: "酒店预订", desc: "合规住宿推荐", color: "from-primary/8 to-primary/3" },
  { icon: UtensilsCrossed, label: "宴请安排", desc: "商务餐厅预订", color: "from-primary/10 to-primary/5" },
  { icon: Receipt, label: "发票识别", desc: "OCR票据处理", color: "from-primary/8 to-primary/3" },
];

export default function WelcomePage() {
  const [input, setInput] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      navigate("/chat", { state: { initialMessage: input } });
    }
  };

  const goToChat = () => navigate("/chat");
  const goToLive = () => navigate("/live");

  return (
    <div className="min-h-screen flex flex-col bg-background relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-primary/5 blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 lg:px-12">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          <span className="font-bold text-lg tracking-tight">智能商旅助手</span>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 pb-8 -mt-8">
        {/* Avatar with breathing effect */}
        <div className="relative mb-6">
          <div className="absolute inset-0 rounded-full bg-primary/10 animate-pulse-ring" />
          <img
            src={avatarFull}
            alt="智能商旅助手"
            className="w-48 h-48 md:w-56 md:h-56 object-contain animate-breathe drop-shadow-lg"
          />
        </div>

        {/* Welcome text */}
        <div className="text-center mb-8 opacity-0 animate-fade-in" style={{ animationDelay: "0.15s" }}>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-balance leading-tight">
            您好，我是您的<span className="text-primary">商旅助手</span>
          </h1>
          <p className="text-muted-foreground mt-3 text-base md:text-lg max-w-md mx-auto text-balance">
            帮您规划行程、预订酒店、安排宴请、处理报销——一切差旅事务交给我
          </p>
        </div>

        {/* Quick action cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10 w-full max-w-2xl opacity-0 animate-fade-in" style={{ animationDelay: "0.3s" }}>
          {quickActions.map(({ icon: Icon, label, desc, color }) => (
            <button
              key={label}
              onClick={goToChat}
              className={`group flex flex-col items-start p-4 rounded-xl border bg-gradient-to-br ${color} hover:shadow-md hover:border-primary/20 transition-all duration-200 active:scale-[0.97] text-left`}
            >
              <Icon className="w-5 h-5 text-primary mb-2 group-hover:scale-110 transition-transform" />
              <span className="font-medium text-sm">{label}</span>
              <span className="text-xs text-muted-foreground mt-0.5">{desc}</span>
            </button>
          ))}
        </div>

        {/* Input bar */}
        <form onSubmit={handleSubmit} className="w-full max-w-2xl opacity-0 animate-fade-in" style={{ animationDelay: "0.45s" }}>
          <div className="flex items-center gap-2 p-2 rounded-2xl border bg-card shadow-lg shadow-primary/5">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="描述您的差旅需求..."
              className="flex-1 bg-transparent px-4 py-3 text-sm outline-none placeholder:text-muted-foreground"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="shrink-0 p-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-all active:scale-95"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* Mode switches */}
        <div className="flex gap-3 mt-6 opacity-0 animate-fade-in" style={{ animationDelay: "0.6s" }}>
          <button
            onClick={goToChat}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border bg-card text-sm font-medium hover:border-primary/30 hover:bg-accent transition-all active:scale-[0.97]"
          >
            <MessageSquare className="w-4 h-4 text-primary" />
            文字对话
          </button>
          <button
            onClick={goToLive}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border bg-card text-sm font-medium hover:border-primary/30 hover:bg-accent transition-all active:scale-[0.97]"
          >
            <Mic className="w-4 h-4 text-primary" />
            LiveTalking
          </button>
        </div>
      </main>
    </div>
  );
}
