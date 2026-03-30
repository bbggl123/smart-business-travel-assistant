# 用户指令记忆

本文件记录了用户的指令、偏好和教导，用于在未来的交互中提供参考。

## 格式

### 用户指令条目
用户指令条目应遵循以下格式：

[用户指令摘要]
- Date: [YYYY-MM-DD]
- Context: [提及的场景或时间]
- Instructions:
  - [用户教导或指示的内容，逐行描述]

### 项目知识条目
Agent 在任务执行过程中发现的条目应遵循以下格式：

[项目知识摘要]
- Date: [YYYY-MM-DD]
- Context: Agent 在执行 [具体任务描述] 时发现
- Category: [代码结构|代码模式|代码生成|构建方法|测试方法|依赖关系|环境配置]
- Instructions:
  - [具体的知识点，逐行描述]

## 去重策略
- 添加新条目前，检查是否存在相似或相同的指令
- 若发现重复，跳过新条目或与已有条目合并
- 合并时，更新上下文或日期信息
- 这有助于避免冗余条目，保持记忆文件整洁

## 条目

### 用户指令

[智能商旅助手项目全面修复与测试]
- Date: 2026-03-30
- Context: 用户要求对智能商旅助手项目进行全面检查和修复修复
- Instructions:
  - 修复前端消息重复渲染问题（chat.py message_end content字段重复）- 已完成
  - 修复Intent Agent宴请字段追问优先级逻辑 - 已完成，当dining_needed=是时优先追问宴请相关字段
  - 修复Transportation Agent火车超标同步推荐机票 - 已完成，添加sync_recommend类别
  - 修复Hotel Agent超标双重推荐逻辑 - 已完成，实现compliant和alternative双重推荐
  - 验证LLM网关和紫东太初API连接 - 已完成，API Key: z0oxh3h9tbeq2gihnvdhq0el
  - 待完成：Dispatcher Agent多Agent协作
  - 待完成：Invoice Agent OCR服务接入
  - 待完成：Mock Data Agent web-content-fetcher集成
  - 待完成：移除正则降级方案
  - 待完成：对话上下文管理增强
  - 待执行：前后端联调测试（至少3轮）

### 项目知识

[后端API Key配置]
- Date: 2026-03-30
- Context: Agent 在检查智能商旅助手项目配置时发现
- Category: 环境配置
- Instructions:
  - 紫东太初API Key位于 `/workspace/backend/.env`
  - ZIDONGTAICHU_API_KEY=z0oxh3h9tbeq2gihnvdhq0el
  - ZIDONGTAICHU_API_URL=https://cloud.zidongtaichu.com/maas/v1/chat/completions
  - ZIDONGTAICHU_MODEL=Kimi-K2.5

[项目技术栈]
- Date: 2026-03-30
- Context: Agent 在分析项目结构时发现
- Category: 代码结构
- Instructions:
  - 前端：React + TypeScript + Vite + TailwindCSS + shadcn/ui
  - 后端：Python + FastAPI + Redis Streams
  - 数据库：Supabase (PostgreSQL + Redis)
  - LLM：紫东太初kimi k2.5 (已配置)
  - 地图服务：高德地图API
  - web-content-fetcher skill路径：`/workspace/web-content-fetcher-main`

[项目Agent架构]
- Date: 2026-03-30
- Context: Agent 在分析项目时发现
- Category: 代码结构
- Instructions:
  - Dispatcher Agent：工作流协调
  - IntentUnderstandingAgent：意图理解（4层COT）
  - TransportationAgent：出行搜索，支持火车贵时推荐机票
  - HotelAgent：酒店搜索，支持超标双重推荐
  - DiningAgent：餐厅搜索，支持超标双重展示
  - ComplianceAgent：合规检查
  - InvoiceAgent：发票识别
  - MockDataAgent：Mock数据生成，集成web-content-fetcher
  - ApprovalAgent：审批单生成

[已修复的问题]
- Date: 2026-03-30
- Context: Agent 在修复智能商旅助手问题时发现并修复
- Category: 代码结构
- Instructions:
  - 前端消息重复渲染：ChatPage.tsx中streamingContent与msg.content渲染逻辑问题，已修复
  - 后端消息重复发送：chat.py中message_end事件content字段与流式content重复，已修复
  - COT引擎类型错误：cot/base.py中BaseCOTAgent方法返回类型声明为dict但实际返回COTLayerResult，已修复
  - Intent Agent类型错误：intent.py中session_id和message可能为None，已添加默认值处理
  - 日期提取增强：LLM日期识别prompt增强，现在可以正确提取"下周三"等相对日期

[测试命令]
- Date: 2026-03-30
- Context: Agent 在检查项目测试时发现
- Category: 测试方法
- Instructions:
  - 后端测试：`cd /workspace/backend && python -m pytest tests/ -v`
  - 前端开发服务器：`cd /workspace && npm run dev` (端口8080)
  - 后端开发服务器：`cd /workspace/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - 健康检查：`curl http://localhost:8000/health`
  - 流式API测试：`curl -X POST http://localhost:8000/api/chat/stream -H "Content-Type: application/json" -d '{"message": "..."}'`
