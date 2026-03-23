# 智能商旅助手 - 启动点确认报告（后端优先版）

**生成日期**: 2026-03-22
**框架版本**: v3.0
**状态**: ✅ 已确认

---

## ⚠️ 开发策略更新 (v3.0)

**后端优先策略**：
1. 先完整开发后端（Phase B + Phase C + Phase D）
2. 测试验证后端 API
3. 再开发前端（Phase A + Phase E + Phase F + Phase G）
4. 最后集成测试（Phase G）

---

## 一、后端优先策略说明

### 1.1 为什么后端优先？

| 优势 | 说明 |
|------|------|
| **接口先行** | 后端 API 确定后，前端开发有明确标准 |
| **避免返工** | 避免接口变更导致的前端返工 |
| **并行开发** | 后端开发期间，前端可以设计 UI 和 Mock 接口 |
| **独立测试** | 后端可以独立测试和验证业务逻辑 |
| **文档完整** | 后端 API 文档完整后，前端开发有据可依 |

### 1.2 开发顺序

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase B: 后端基础设施                      │
│              (Week 1: LLM网关 + 数据库模型)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase C: Agent 开发                       │
│           (Week 2-3: Dispatcher + Intent + 各专业Agent)     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase D: 审批与发票                       │
│                   (Week 4: Approval + Invoice)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase B-C-D: 测试                         │
│                  (Week 4-5: API测试 + 联调)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase A: 前端核心架构                      │
│              (Week 5-6: API层 + 状态管理 + WebSocket)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase E: 前端交互流程                      │
│               (Week 6-7: 意图理解 + 方案推荐)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase F: COT 展示                         │
│                    (Week 7: 思维链可视化)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Phase G: 集成与优化                        │
│                    (Week 8: 集成 + 性能优化)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、技术架构确认

### 2.1 技术栈

| 层级 | 技术 | 状态 |
|------|------|------|
| **后端** | Python + FastAPI | ⏳ 待开发 |
| **数据库** | Supabase PostgreSQL | ✅ 已配置 |
| **缓存** | Supabase Redis | ✅ 已配置 |
| **LLM** | 紫东太初 Kimi-K2.5 | ✅ 已获取API |
| **前端** | React + TypeScript + Vite | ✅ 已就绪 |
| **前端UI** | TailwindCSS + shadcn/ui | ✅ 已就绪 |

### 2.2 资源确认

| 资源 | 状态 | 凭证 |
|------|------|------|
| 紫东太初 API | ✅ 已获取 | `z0oxh3h9tbeq2gihnvdhq0el` |
| 高德地图 API | ✅ 已获取 | `8d1fd7a0ea3fbd4053e853cefac9d175` |
| Supabase | ✅ 已配置 | 项目: `bbggdllll21@2925.com's Project` |

---

## 三、执行计划（后端优先）

### 3.1 Week 1: Phase B - 后端基础设施

**目标**: 完成 LLM 网关和数据库模型

| Day | 任务 | Task ID |
|-----|------|---------|
| 1-2 | 创建后端目录结构 | B1-T001 |
| 1-2 | 配置 Python 环境 | B1-T002 |
| 1-2 | 配置 Supabase 连接 | B1-T003 |
| 1-2 | 配置日志系统 | B1-T004 |
| 3-4 | 实现 Provider 抽象层 | B2-T001 |
| 3-4 | 实现紫东太初 Provider | B2-T002 |
| 5 | 实现统一网关 | B2-T003 |
| 5 | 实现错误处理和重试 | B2-T004 |
| 6-7 | 实现 User/Session/Message 模型 | B3-T001~003 |
| 8 | 实现 Trip/Booking 模型 | B3-T004~005 |

### 3.2 Week 2-3: Phase C - Agent 开发

**目标**: 完成所有 Agent 开发

| Day | 任务 | Task ID |
|-----|------|---------|
| 9-10 | 实现消息接收 | C1-T001 |
| 10-11 | 实现工作流创建 | C1-T002 |
| 11-12 | 实现任务分发 | C1-T003 |
| 12-13 | 实现结果聚合 | C1-T004 |
| 14-15 | 实现语义解析 | C2-T001 |
| 15-16 | 实现意图分类 | C2-T002 |
| 16-17 | 实现信息提取 | C2-T003 |
| 17-18 | 实现追问生成 | C2-T004 |
| 18-19 | 实现上下文管理 | C2-T005 |
| 20-21 | 实现航班/火车搜索 | C3-T001~002 |
| 21-22 | 实现方案推荐 | C3-T003 |
| 22-23 | 实现预订功能 | C3-T004 |
| 23-24 | 实现酒店搜索 | C4-T001 |
| 24-25 | 实现距离计算/双重推荐 | C4-T002~003 |
| 25-26 | 实现餐厅搜索 | C5-T001 |
| 26-27 | 实现菜品推荐/双重展示 | C5-T002~003 |
| 27-28 | 实现规则引擎 | C6-T001 |
| 28-29 | 实现交通/住宿合规检查 | C6-T002~003 |
| 29-30 | 实现餐饮合规检查 | C6-T004 |
| 30 | 生成合规报告 | C6-T005 |

### 3.3 Week 4: Phase D - 审批与发票 + 测试

**目标**: 完成审批发票 Agent，并开始测试

| Day | 任务 | Task ID |
|-----|------|---------|
| 31-32 | 实现数据汇总 | D1-T001 |
| 32-33 | 实现审批单生成 | D1-T002 |
| 33-34 | 实现 PDF 导出 | D1-T003 |
| 34 | 实现打印支持 | D1-T004 |
| 35-36 | 实现发票上传 | D2-T001 |
| 36-37 | 实现 OCR 识别 | D2-T002 |
| 37-38 | 实现字段提取 | D2-T003 |
| 38-39 | 实现批量处理 | D2-T004 |
| 39-40 | API 接口测试 | TEST-001 |
| 40-41 | WebSocket 测试 | TEST-002 |
| 41-42 | Agent 协作测试 | TEST-003 |
| 42-43 | Mock 数据验证 | TEST-004 |

### 3.4 Week 5-8: Phase A-F - 前端开发 + 集成

**目标**: 完成前端开发和集成

| Week | Phase | 任务 |
|------|-------|------|
| Week 5 | Phase A | 前端核心架构 |
| Week 6 | Phase A + E | 状态管理 + WebSocket + 交互流程 |
| Week 7 | Phase E + F | 方案推荐 + COT展示 |
| Week 8 | Phase G | 集成 + 优化 |

---

## 四、检查点设置

| 检查点 | 时机 | 评审内容 | 通过标准 |
|--------|------|----------|----------|
| Checkpoint-B | Day 8 | 后端基础设施 | LLM调用成功 + DB连接正常 |
| Checkpoint-C | Day 30 | Agent 开发 | 所有 Agent 功能正常 |
| Checkpoint-D | Day 39 | 审批与发票 | 功能完整 |
| Checkpoint-TEST | Day 43 | 后端测试 | 所有测试通过 |
| Checkpoint-A | Day 48 | 前端核心架构 | API层 + 状态管理正常 |
| Checkpoint-E | Day 54 | 前端交互流程 | 追问 + 方案展示正常 |
| Checkpoint-F | Day 58 | COT 展示 | 思维链可视化正常 |
| Checkpoint-G | Day 64 | 集成优化 | 全流程测试通过 |

---

## 五、后端 API 规范（初步）

### 5.1 Chat API

```python
# POST /api/chat/send
Request: {
    "session_id": str,
    "message": str
}
Response: {
    "code": 0,
    "message": "success",
    "data": {
        "message_id": str,
        "content": str,
        "agent_id": str,
        "card_type": str | null
    }
}
```

### 5.2 Intent API

```python
# POST /api/intent/parse
Request: {
    "session_id": str,
    "message": str
}
Response: {
    "code": 0,
    "data": {
        "intent_type": str,  # "trip_planning" | "invoice" | "mock_data"
        "entities": {
            "departure": str | null,
            "destination": str | null,
            "start_date": str | null,
            "end_date": str | null,
            "headcount": int | null,
            "user_level": str | null,
            "purpose": str | null
        },
        "missing_fields": [str],
        "questions": [
            {"field": str, "question": str, "options": [str] | null}
        ]
    }
}

# POST /api/intent/clarify
Request: {
    "session_id": str,
    "answers": {field: value}
}
Response: same as parse
```

### 5.3 Transport API

```python
# POST /api/transport/search
Request: {
    "departure": str,
    "destination": str,
    "date": str,
    "type": str  # "flight" | "train" | "both"
}
Response: {
    "code": 0,
    "data": [
        {
            "id": str,
            "type": str,
            "provider": str,
            "flight_no": str | null,
            "departure": {"city": str, "code": str, "time": str},
            "arrival": {"city": str, "code": str, "time": str},
            "duration": str,
            "price": float,
            "compliance": {
                "is_compliant": bool,
                "reason": str | null
            }
        }
    ]
}

# POST /api/transport/book
Request: {"option_id": str}
Response: {
    "code": 0,
    "data": {
        "booking_id": str,
        "status": str,
        "message": str
    }
}
```

### 5.4 Hotel API

```python
# POST /api/hotel/search
Request: {
    "city": str,
    "check_in": str,
    "check_out": str,
    "star": int | null
}
Response: {
    "code": 0,
    "data": [
        {
            "id": str,
            "name": str,
            "stars": int,
            "price": float,
            "distance_km": float,
            "compliance": {
                "is_compliant": bool,
                "limit": float,
                "over_budget": float | null,
                "alternatives": [HotelOption]
            }
        }
    ]
}
```

### 5.5 Dining API

```python
# POST /api/dining/search
Request: {
    "city": str,
    "date": str,
    "headcount": int,
    "cuisine": str | null,
    "budget_per_person": float | null
}
Response: {
    "code": 0,
    "data": [
        {
            "id": str,
            "restaurant": str,
            "cuisine": str,
            "price_per_person": float,
            "total_amount": float,
            "has_private_room": bool,
            "recommended_dishes": [
                {"name": str, "price": float, "suitable_for": int}
            ],
            "compliance": {
                "is_compliant": bool,
                "limit": float,
                "over_budget": float | null
            }
        }
    ]
}
```

### 5.6 Approval API

```python
# POST /api/approval/generate
Request: {"trip_id": str}
Response: {
    "code": 0,
    "data": {
        "approval_id": str,
        "employee": {
            "name": str,
            "level": str,
            "department": str
        },
        "trip": {...},
        "items": [
            {"category": str, "name": str, "amount": float, "is_compliant": bool}
        ],
        "total_amount": float,
        "status": str,
        "pdf_url": str
    }
}

# GET /api/approval/{approval_id}/pdf
Response: PDF文件流
```

### 5.7 Invoice API

```python
# POST /api/invoice/upload
Request: FormData(files: File[])
Response: {
    "code": 0,
    "data": [
        {
            "invoice_id": str,
            "status": str,
            "fields": {
                "invoice_code": str,
                "invoice_number": str,
                "invoice_date": str,
                "buyer_name": str,
                "seller_name": str,
                "total_amount": float,
                "tax_rate": float
            },
            "confidence": {field: float},
            "low_confidence_fields": [str]
        }
    ]
}

# POST /api/invoice/confirm
Request: {
    "invoice_id": str,
    "fields": {field: value}
}
Response: {"code": 0}
```

---

## 六、结论

### ✅ 启动点确认通过

**可以开始 Phase B: 后端基础设施 开发**

### 下一步行动

```bash
# 1. 创建后端目录结构
mkdir -p backend/app/api/routes backend/app/agents backend/app/llm/providers backend/app/services backend/app/storage backend/app/utils

# 2. 配置 Python 环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn supabase redis python-dotenv pydantic

# 3. 开始后端开发
```

---

**预计完成全部开发所需时间**: 8周 (269小时)

**文档版本**: v3.0 (后端优先版)
**维护者**: ProjectManager Agent
**下次评审**: Day 8 (Checkpoint-B)