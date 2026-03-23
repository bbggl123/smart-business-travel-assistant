# 技术设计文档 - 智能商旅助手

## 引言

本文档是智能商旅助手系统的技术设计规格说明书，描述了系统的技术架构、Agent设计、数据模型和接口定义。

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **API层** | Python + FastAPI | 统一入口、身份认证、请求路由 |
| **Agent协作** | 消息队列（Redis Streams） | Agent间异步通信、任务分发 |
| **数据存储** | Supabase (PostgreSQL + Redis) | 会话状态、差标规则、审批单存储 |
| **前端** | Web聊天界面 + 企业微信/飞书/钉钉 | 多渠道用户交互 |
| **LLM集成** | 多LLM网关（紫东太初kimi k2.5 + 备用） | 统一调用、故障切换 |

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  Web Chat   │    │  企业微信    │    │   飞书      │          │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│         │                  │                  │                  │
│  ┌─────────────┐                           ┌─────────────┐      │
│  │    钉钉     │                           │   企业微信   │      │
│  └──────┬──────┘                           └──────┬──────┘      │
└─────────┼────────────────────────────────────┼─────────────────┘
          │                                    │
          └──────────────────┬─────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                      │
│  - 统一入口                                                      │
│  - 身份认证                                                      │
│  - 请求路由                                                      │
└─────────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Dispatcher     │ │  WebSocket      │ │  HTTP API       │
│  Agent          │ │  Handler        │ │  Handler        │
└────────┬────────┘ └─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Message Queue (Redis Streams)                │
│  - Agent间异步通信                                               │
│  - 任务分发                                                      │
│  - 结果回调                                                      │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Workers (并发执行)                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ Intent  │ │Transport│ │  Hotel  │ │ Dining  │ │Approval │     │
│  │Agent    │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase (PostgreSQL + Redis)              │
│  - 会话状态                                                      │
│  - 差标规则                                                      │
│  - 审批单存储                                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Agent 角色矩阵

| Agent | 职责 | 输入 | 输出 | 并行能力 |
|-------|------|------|------|----------|
| **Dispatcher** | 工作流协调 | 用户消息 | 任务分发 | 入口 |
| **Intent Understanding** | 语义理解、信息补全 | 原始消息+上下文 | 结构化意图 | 单Agent |
| **Transportation** | 出行搜索+预订 | 行程需求 | 方案列表 | 可并行 |
| **Hotel** | 酒店搜索+预订 | 住宿需求 | 方案列表 | 可并行 |
| **Dining** | 餐厅搜索+推荐 | 宴请需求 | 方案列表 | 可并行 |
| **Compliance** | 差标校验 | 费用项+职级 | 合规结果 | 被调用 |
| **Invoice** | 发票识别 | 图片/PDF | 发票字段 | 单Agent |
| **Approval Form** | 审批单生成 | 汇总数据 | HTML/PDF | 最终汇总 |
| **Mock Data** | 测试数据生成 | 数据类型 | Mock数据集 | 独立 |

## Agent 内部设计

### 每个 Agent 的通用结构

每个 Agent 内部采用 **COT (Chain of Thought)** 框架：

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Worker                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Input Handler (输入处理)                │   │
│  │   - 消息反序列化                                      │   │
│  │   - 上下文注入                                        │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              COT Engine (思维链引擎)                   │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │   │ Intent     │  │ Knowledge   │  │ Reasoning   │  │   │
│  │   │ Understanding│→│ Retrieval  │→│ Decision   │  │   │
│  │   │ Layer      │  │ Layer       │  │ Layer      │  │   │
│  │   └─────────────┘  └─────────────┘  └──────┬──────┘  │   │
│  │                                            │         │   │
│  │                           ┌────────────────▼───┐     │   │
│  │                           │ Response Generator  │     │   │
│  │                           │ Layer (响应生成)   │     │   │
│  │                           └─────────────────────┘     │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Output Handler (输出处理)               │   │
│  │   - 结果序列化                                        │   │
│  │   - 发布到消息队列                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### COT 各层职责

| 层级 | 职责 | 输入 | 输出 |
|------|------|------|------|
| **Intent Understanding** | 解析用户自然语言，提取语义 | 原始消息 + 上下文 | 结构化意图对象 |
| **Knowledge Retrieval** | 检索差旅政策、公司规定、历史案例 | 意图对象 | 相关知识片段 |
| **Reasoning Decision** | 多步推理，生成决策 | 意图 + 知识 | 决策 + 依据 |
| **Response Generator** | 生成自然语言响应 | 决策 | 格式化响应 |

### 示例：Intent Understanding Agent COT 流程

```
用户输入: "我想下周去深圳见客户，呆两天"

COT Step 1 - 语义解析:
  → 识别动作: 出差 (travel)
  → 实体提取: 目的地=深圳, 时间=下周, 人数=1, 时长=2天
  → 隐含信息: 见客户 → 商务出差

COT Step 2 - 意图分类:
  → 意图类型: NEW_TRIP_REQUEST
  → 置信度: 0.92
  → 缺失字段: [出发地, 职级, 出行方式, 住宿要求]

COT Step 3 - 完整性检查:
  → 必填字段: 出发地, 目的地, 时间, 职级, 出行方式
  → 缺失: 出发地, 职级
  → 生成追问: ["请问您从哪个城市出发？", "您的职级是？"]

COT Step 4 - 上下文更新:
  → 更新会话状态
  → 通知 Dispatcher 等待用户补全信息
```

## 消息通信协议

### 统一消息格式

```python
class AgentMessage(BaseModel):
    msg_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    task_id: str
    source_agent: AgentType
    target_agent: AgentType | None = None  # None = 广播
    msg_type: MessageType  # REQUEST, RESPONSE, BROADCAST, HEARTBEAT
    payload: dict
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_count: int = 0

# 消息类型
class MessageType(str, Enum):
    REQUEST = "request"           # 请求执行任务
    RESPONSE = "response"         # 返回结果
    BROADCAST = "broadcast"       # 广播消息
    HEARTBEAT = "heartbeat"       # 心跳检测
    COMPLIANCE_CHECK = "compliance_check"  # 合规检查请求
    COMPLIANCE_RESULT = "compliance_result"  # 合规检查结果
```

### 工作流类型定义

```python
class WorkflowType(str, Enum):
    TRIP_PLANNING = "trip_planning"      # 行程规划
    INVOICE_PROCESSING = "invoice"       # 发票处理
    MOCK_DATA_GENERATION = "mock_data"   # Mock数据生成
    APPROVAL_GENERATION = "approval"     # 审批单生成

# 行程规划工作流
WORKFLOW_TRIP_PLANNING = {
    "steps": [
        {"agent": "intent", "action": "parse", "required": True},
        {"agent": "intent", "action": "fill_missing", "required": False},
        {"agent": "transportation", "action": "search", "parallel": True},
        {"agent": "hotel", "action": "search", "parallel": True},
        {"agent": "dining", "action": "search", "parallel": True, "required": False},
        {"agent": "compliance", "action": "check", "after": ["transportation", "hotel", "dining"]},
        {"agent": "approval", "action": "generate"},
    ]
}
```

## 各 Agent 核心接口

### 1. Dispatcher Agent

```python
class DispatcherAgent:
    async def receive_user_message(self, session_id: str, message: str) -> AgentMessage:
        """接收用户消息，触发工作流"""
        
    async def create_workflow(self, intent: IntentData) -> Workflow:
        """根据意图创建工作流"""
        
    async def dispatch_task(self, task: Task) -> TaskResult:
        """分发任务到指定Agent"""
        
    async def aggregate_results(self, workflow_id: str) -> AggregatedResult:
        """聚合多Agent结果"""
```

### 2. Intent Understanding Agent

```python
class IntentUnderstandingAgent:
    async def parse_semantics(self, message: str, context: dict) -> ParsedIntent:
        """COT推理：解析用户语义"""
        
    async def check_completeness(self, intent: ParsedIntent) -> CompletenessResult:
        """检查信息完整性"""
        
    async def generate_questions(self, missing_fields: list) -> list[Question]:
        """生成追问问题（每轮最多3个）"""
        
    async def update_context(self, session_id: str, field: str, value: any):
        """更新会话上下文"""
```

**COT 推理输出格式**：

```python
class ParsedIntent(BaseModel):
    intent_type: WorkflowType
    entities: Entities
    confidence: float
    reasoning_chain: list[str]
    missing_fields: list[str]
    questions_to_ask: list[Question]

class Entities(BaseModel):
    destination: str | None
    departure: str | None
    start_date: date | None
    end_date: date | None
    headcount: int | None
    user_level: str | None
    purpose: str | None
    transport_preference: str | None
    hotel_requirements: HotelRequirements | None
    dining_requirements: DiningRequirements | None
```

### 3. Transportation Agent

```python
class TransportationAgent:
    async def search_flights(self, req: FlightSearchReq) -> list[FlightOption]:
        """搜索航班"""
        
    async def search_trains(self, req: TrainSearchReq) -> list[TrainOption]:
        """搜索火车票"""
        
    async def calculate_compliance(self, option: TransportOption, user_level: str) -> ComplianceResult:
        """调用Compliance Agent检查合规性"""
        
    async def generate_recommendation(self, options: list[TransportOption], user_pref: str) -> TravelRecommendation:
        """生成出行推荐报告"""
        
    async def book_ticket(self, option: TransportOption) -> BookingResult:
        """预订机票/火车票（Mock）"""
```

### 4. Hotel Agent

```python
class HotelAgent:
    async def search_hotels(self, req: HotelSearchReq) -> list[HotelOption]:
        """搜索酒店"""
        
    async def calculate_distance(self, hotel: HotelOption, customer_location: str) -> float:
        """计算酒店与客户位置的距离（公里）"""
        
    async def check_compliance(self, hotel: HotelOption, user_level: str, city_tier: int) -> ComplianceResult:
        """调用Compliance Agent检查合规性"""
        
    async def generate_recommendation(self, options: list[HotelOption], user_req: HotelRequirements) -> HotelRecommendation:
        """生成酒店推荐报告（含替代方案）"""
        
    async def book_hotel(self, option: HotelOption) -> BookingResult:
        """预订酒店（Mock）"""
```

### 5. Dining Agent

```python
class DiningAgent:
    async def search_restaurants(self, req: DiningSearchReq) -> list[RestaurantOption]:
        """搜索餐厅"""
        
    async def suggest_dishes(self, restaurant: RestaurantOption, headcount: int) -> list[Dish]:
        """推荐匹配宴请人数的菜品"""
        
    async def check_compliance(self, dining: DiningOption, user_level: str) -> ComplianceResult:
        """调用Compliance Agent检查合规性"""
        
    async def generate_recommendation(self, options: list[RestaurantOption], user_req: DiningRequirements) -> DiningRecommendation:
        """生成宴请推荐报告"""
        
    async def reserve_restaurant(self, option: DiningOption) -> BookingResult:
        """预订餐厅（Mock）"""
```

### 6. Compliance Agent

```python
class ComplianceAgent:
    def __init__(self, rules: TravelStandardRules):
        """初始化差标规则引擎"""
        
    async def check_flight(self, price: Decimal, user_level: str) -> FlightComplianceResult:
        """检查机票是否合规"""
        
    async def check_train(self, price: Decimal, user_level: str) -> TrainComplianceResult:
        """检查火车票是否合规"""
        
    async def check_hotel(self, price: Decimal, user_level: str, city_tier: int) -> HotelComplianceResult:
        """检查酒店是否合规（按城市级别）"""
        
    async def check_dinner(self, per_person: Decimal, user_level: str) -> DinnerComplianceResult:
        """检查宴请人均是否合规"""
        
    async def generate_report(self, checks: list[ComplianceResult]) -> ComplianceReport:
        """生成综合合规报告"""
```

**差标规则定义**：

```python
class TravelStandardRules:
    """差旅标准规则库（示例）"""
    
    RULES = {
        "P1": {
            "flight": Decimal("3000"),
            "train": Decimal("1000"),
            "hotel": {"1st_tier": Decimal("600"), "2nd_tier": Decimal("450"), "3rd_tier": Decimal("300")},
            "dinner_per_person": Decimal("200")
        },
        "P2": {
            "flight": Decimal("5000"),
            "train": Decimal("1500"),
            "hotel": {"1st_tier": Decimal("900"), "2nd_tier": Decimal("650"), "3rd_tier": Decimal("400")},
            "dinner_per_person": Decimal("300")
        },
        "M1": {
            "flight": Decimal("8000"),
            "train": Decimal("2000"),
            "hotel": {"1st_tier": Decimal("1200"), "2nd_tier": Decimal("900"), "3rd_tier": Decimal("600")},
            "dinner_per_person": Decimal("500")
        },
        "M2": {
            "flight": Decimal("12000"),
            "train": Decimal("2500"),
            "hotel": {"1st_tier": Decimal("1800"), "2nd_tier": Decimal("1400"), "3rd_tier": Decimal("900")},
            "dinner_per_person": Decimal("800")
        }
    }
    
    CITY_TIER_MAP = {
        "1st_tier": ["北京", "上海", "广州", "深圳"],
        "2nd_tier": ["杭州", "成都", "南京", "武汉", "西安", "苏州", "天津", "重庆", "长沙"],
        "3rd_tier": ["其他地级市"]
    }
```

### 7. Invoice Agent

```python
class InvoiceAgent:
    async def extract_from_image(self, image_data: bytes) -> InvoiceFields:
        """OCR + 多模态LLM 双重校验识别"""
        
    async def extract_from_pdf(self, pdf_data: bytes) -> InvoiceFields:
        """PDF 发票提取"""
        
    async def validate_fields(self, fields: InvoiceFields) -> ValidationResult:
        """字段校验与置信度评估"""
        
    async def batch_process(self, files: list[FileData]) -> list[InvoiceResult]:
        """批量处理多张发票"""
        
    async def generate_draft(self, invoices: list[InvoiceResult]) -> ExpenseDraft:
        """生成报销信息草稿"""
```

**发票识别流程**：

```
用户上传发票图片/PDF
        ↓
┌─────────────────────────────────────────┐
│           OCR 引擎识别                    │
│   (提取文字、表格结构、关键字段)            │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         多模态 LLM 校验                   │
│   (紫东太初kimi k2.5)                    │
│   - 字段纠错                              │
│   - 格式标准化                            │
│   - 语义理解                              │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          置信度评估                       │
│   - 高置信度 → 自动填充                   │
│   - 低置信度 → 标记"待确认"               │
└─────────────────┬───────────────────────┘
                  ↓
          输出结构化发票字段
```

### 8. Approval Form Agent

```python
class ApprovalFormAgent:
    async def aggregate_trip_data(self, trip_id: str) -> TripSummary:
        """汇总行程数据"""
        
    async def generate_html(self, summary: TripSummary) -> str:
        """生成审批单HTML"""
        
    async def convert_to_pdf(self, html: str) -> bytes:
        """HTML转PDF"""
        
    async def upload_and_get_url(self, pdf_data: bytes) -> str:
        """上传PDF并返回URL"""
        
    async def create_approval_record(self, trip_id: str, pdf_url: str) -> ApprovalRecord:
        """创建审批记录"""
```

### 9. Mock Data Agent

```python
class MockDataAgent:
    def __init__(self, web_fetcher: WebContentFetcher):
        self.fetcher = web_fetcher
        
    async def fetch_real_flights(self, route: Route) -> list[Flight]:
        """调用web-content-fetcher获取真实航班数据"""
        
    async def fetch_real_hotels(self, city: str, check_in: date, check_out: date) -> list[Hotel]:
        """调用web-content-fetcher获取真实酒店数据"""
        
    async def fetch_real_trains(self, route: Route, date: date) -> list[Train]:
        """调用web-content-fetcher获取真实火车数据"""
        
    async def fetch_real_restaurants(self, city: str, cuisine: str | None) -> list[Restaurant]:
        """调用web-content-fetcher获取真实餐厅数据"""
        
    async def generate_mock_dataset(self, real_data: list, variants: int = 10) -> list:
        """基于真实数据生成1:1 Mock数据集"""
        
    async def export_to_json(self, dataset: list, filename: str) -> str:
        """导出为JSON格式"""
```

## 数据模型设计

### 核心实体关系

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Session      │────→│   Message       │     │    User         │
│    会话         │     │    消息         │     │    用户         │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ user_id (FK)    │     │ session_id (FK) │     │ name            │
│ status          │     │ role            │     │ level           │
│ context (JSON)  │     │ content         │     │ department      │
│ created_at      │     │ intent_data     │     │ travel_std_id   │
│ updated_at      │     │ created_at      │     │ created_at      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  TravelStd      │     │    Trip         │     │   Approval      │
│  差旅标准        │←────│    出差计划      │────→│   审批单        │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ level           │     │ user_id (FK)    │     │ trip_id (FK)    │
│ flight_limit    │     │ purpose         │     │ status          │
│ train_limit     │     │ status          │     │ total_amount    │
│ hotel_limit_1st │     │ destination     │     │ pdf_url         │
│ hotel_limit_2nd │     │ departure       │     │ created_at      │
│ hotel_limit_3rd │     │ start_date      │     │ approved_at     │
│ dinner_limit    │     │ end_date        │     │ approver_id     │
│ city_tier_map    │     │ created_at      │     └─────────────────┘
└─────────────────┘     └────────┬────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Transportation │     │    Hotel      │     │    Dining     │
│   出行方案     │     │   住宿方案    │     │   宴请方案    │
├───────────────┤     ├───────────────┤     ├───────────────┤
│ id (PK)       │     │ id (PK)       │     │ id (PK)       │
│ trip_id (FK)  │     │ trip_id (FK)  │     │ trip_id (FK)  │
│ type          │     │ name          │     │ restaurant    │
│ provider      │     │ city          │     │ cuisine       │
│ flight_no     │     │ star          │     │ date          │
│ departure     │     │ price         │     │ headcount     │
│ destination   │     │ distance_km   │     │ per_person    │
│ depart_time   │     │ is_compliant  │     │ total_amount  │
│ arrive_time   │     └───────────────┘     │ is_compliant  │
│ price         │                           └───────────────┘
│ is_compliant  │
└───────────────┘
```

### Supabase 表结构定义

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    travel_std_id UUID REFERENCES travel_standards(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 差旅标准表
CREATE TABLE travel_standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(50) NOT NULL UNIQUE,
    flight_limit DECIMAL(10,2),
    train_limit DECIMAL(10,2),
    hotel_limit_1st_city DECIMAL(10,2),
    hotel_limit_2nd_city DECIMAL(10,2),
    hotel_limit_3rd_city DECIMAL(10,2),
    dinner_limit_per_person DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 会话表
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id),
    role VARCHAR(20) NOT NULL,
    agent_type VARCHAR(50),
    content TEXT NOT NULL,
    intent_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 出差计划表
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID REFERENCES sessions(id),
    purpose TEXT,
    status VARCHAR(20) DEFAULT 'planning',
    destination VARCHAR(100),
    departure VARCHAR(100),
    start_date DATE,
    end_date DATE,
    transportation_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 出行方案表
CREATE TABLE transportations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    type VARCHAR(20) NOT NULL,
    provider VARCHAR(50),
    flight_no VARCHAR(20),
    departure VARCHAR(100),
    destination VARCHAR(100),
    depart_time TIMESTAMP,
    arrive_time TIMESTAMP,
    price DECIMAL(10,2),
    is_compliant BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 酒店方案表
CREATE TABLE hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    name VARCHAR(200) NOT NULL,
    city VARCHAR(50),
    star INTEGER,
    price DECIMAL(10,2),
    distance_km DECIMAL(5,2),
    address TEXT,
    facilities TEXT[],
    is_compliant BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 宴请方案表
CREATE TABLE dinings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    restaurant VARCHAR(200) NOT NULL,
    cuisine VARCHAR(50),
    city VARCHAR(50),
    date DATE,
    headcount INTEGER,
    per_person DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    dishes JSONB,
    is_compliant BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 审批单表
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(12,2),
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    approver_id UUID REFERENCES users(id)
);
```

### Redis 数据结构（会话缓存）

```
# 会话上下文 (Hash)
session:{session_id}:context = {
    "user_info": {...},
    "trip_requirements": {...},
    "collected_fields": ["destination", "dates"],
    "missing_fields": ["departure", "level"]
}

# Agent 任务状态 (Hash)
task:{task_id}:status = {
    "agent": "transport",
    "status": "processing",
    "progress": 0.6,
    "result": null,
    "error": null
}

# 消息队列stream (Stream)
agents:queue:{agent_type} = [
    {id, message, session_id, task_id, timestamp}
]
```

## 核心设计原则

1. **Agent 独立性**：每个Agent是独立的工作进程，通过消息队列通信
2. **异步非阻塞**：用户请求立即返回任务ID，通过WebSocket推送进度
3. **状态外置**：会话状态存储在Redis，Agent无状态设计
4. **可插拔**：新增Agent只需订阅对应消息队列，无需修改核心代码
5. **COT推理**：每个Agent内部实现思维链，确保推理可复现
