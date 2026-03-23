import {
  CalendarRange, Plane, Hotel, UtensilsCrossed, FileCheck, Receipt, ShieldCheck, ClipboardList, Sparkles
} from "lucide-react";

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: any;
  color: string;
}

export const agents: Agent[] = [
  { id: "smart", name: "智能协作", description: "多Agent自动调度", icon: Sparkles, color: "hsl(18 100% 59%)" },
  { id: "scheduler", name: "调度中心", description: "统筹协调各Agent", icon: CalendarRange, color: "hsl(25 95% 55%)" },
  { id: "travel", name: "行程规划", description: "出差路线与日程", icon: Plane, color: "hsl(18 100% 59%)" },
  { id: "hotel", name: "酒店预订", description: "住宿搜索与推荐", icon: Hotel, color: "hsl(30 90% 50%)" },
  { id: "dining", name: "宴请安排", description: "餐厅推荐与预订", icon: UtensilsCrossed, color: "hsl(12 90% 55%)" },
  { id: "compliance", name: "合规审查", description: "费用标准检查", icon: ShieldCheck, color: "hsl(35 85% 50%)" },
  { id: "invoice", name: "发票识别", description: "票据OCR与验证", icon: Receipt, color: "hsl(20 85% 55%)" },
  { id: "approval", name: "审批单", description: "生成审批文档", icon: ClipboardList, color: "hsl(15 90% 52%)" },
];

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentId?: string;
  timestamp: Date;
  card?: MessageCard;
}

export interface MessageCard {
  type: "flight" | "hotel" | "restaurant" | "approval" | "compliance";
  data: any;
}

export const mockFlightCard: MessageCard = {
  type: "flight",
  data: {
    from: "北京",
    fromCode: "PEK",
    to: "上海",
    toCode: "SHA",
    date: "2026-03-25",
    departure: "08:30",
    arrival: "10:50",
    airline: "东方航空 MU5101",
    price: 1280,
    compliant: true,
  },
};

export const mockHotelCard: MessageCard = {
  type: "hotel",
  data: {
    name: "上海浦东丽思卡尔顿酒店",
    stars: 5,
    price: 850,
    distance: "距会议地点 1.2km",
    compliant: false,
    overBudget: 150,
    image: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400&h=250&fit=crop",
  },
};

export const mockRestaurantCard: MessageCard = {
  type: "restaurant",
  data: {
    name: "南京大排档（陆家嘴店）",
    cuisine: "淮扬菜",
    pricePerPerson: 180,
    hasPrivateRoom: true,
    capacity: "8-12人",
    rating: 4.7,
  },
};

export const mockApprovalCard: MessageCard = {
  type: "approval",
  data: {
    items: [
      { name: "机票（往返）", amount: 2560 },
      { name: "酒店（2晚）", amount: 1400 },
      { name: "商务宴请", amount: 2160 },
      { name: "市内交通", amount: 320 },
    ],
    total: 6440,
    status: "待提交",
  },
};

export const mockComplianceCard: MessageCard = {
  type: "compliance",
  data: {
    level: "warning",
    message: "酒店费用超标",
    detail: "您选择的酒店每晚 ¥850，超出差旅标准 ¥700/晚。",
    suggestion: "推荐：上海浦东假日酒店 ¥680/晚，距会议地点 1.5km",
  },
};

export const mockConversation: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "我需要下周三去上海出差，参加一个客户会议，预计两天。帮我安排一下行程。",
    timestamp: new Date("2026-03-21T09:00:00"),
  },
  {
    id: "2",
    role: "assistant",
    content: "好的！我来为您统筹安排上海出差行程。我已经为您搜索了合适的航班方案：",
    agentId: "travel",
    timestamp: new Date("2026-03-21T09:00:05"),
    card: mockFlightCard,
  },
  {
    id: "3",
    role: "assistant",
    content: "同时为您推荐了会议地点附近的酒店：",
    agentId: "hotel",
    timestamp: new Date("2026-03-21T09:00:08"),
    card: mockHotelCard,
  },
  {
    id: "4",
    role: "assistant",
    content: "⚠️ 合规提醒：部分费用需要注意",
    agentId: "compliance",
    timestamp: new Date("2026-03-21T09:00:10"),
    card: mockComplianceCard,
  },
  {
    id: "5",
    role: "user",
    content: "换一个合规的酒店吧。另外帮我找一个适合商务宴请的餐厅，大概8个人。",
    timestamp: new Date("2026-03-21T09:01:00"),
  },
  {
    id: "6",
    role: "assistant",
    content: "没问题！为您推荐一家适合商务宴请的餐厅：",
    agentId: "dining",
    timestamp: new Date("2026-03-21T09:01:05"),
    card: mockRestaurantCard,
  },
  {
    id: "7",
    role: "assistant",
    content: "以下是本次出差的费用汇总审批单，请确认后提交：",
    agentId: "approval",
    timestamp: new Date("2026-03-21T09:01:10"),
    card: mockApprovalCard,
  },
];

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  agentIds: string[];
}

export const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    title: "上海出差行程安排",
    lastMessage: "费用汇总审批单已生成",
    timestamp: new Date("2026-03-21T09:01:10"),
    agentIds: ["travel", "hotel", "dining", "compliance", "approval"],
  },
  {
    id: "conv-2",
    title: "深圳客户拜访",
    lastMessage: "已预订东方航空往返机票",
    timestamp: new Date("2026-03-20T14:30:00"),
    agentIds: ["travel", "hotel"],
  },
  {
    id: "conv-3",
    title: "季度报销审核",
    lastMessage: "3张发票识别完成，2张异常",
    timestamp: new Date("2026-03-19T16:45:00"),
    agentIds: ["invoice", "compliance"],
  },
];
