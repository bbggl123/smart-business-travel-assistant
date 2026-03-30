# 智能商旅助手 - 待办清单

## P0 优先级（核心功能）

### TODO-001: 前端消息重复渲染问题
- **文件**: `src/hooks/useChat.ts`
- **问题**: 流式响应结束后 `streamingContent` 未清理为 null
- **位置**: 第192-194行
- **状态**: 待修复
- **验证**: 测试流式响应结束后消息是否只显示一次

### TODO-002: Intent Agent 宴请字段追问不完整
- **文件**: `backend/app/agents/intent.py`
- **问题**: 缺少宴请相关字段追问（dining_date, dining_location, dietary_requirements, dining_budget）
- **位置**: 第211-230行
- **状态**: 待修复
- **验证**: 测试当用户说"要去出差"时，AI是否追问所有必要字段

### TODO-003: Transportation Agent 火车超标未推荐机票
- **文件**: `backend/app/agents/transportation.py`
- **问题**: 用户期望火车但火车贵时，未同步推荐便宜机票
- **位置**: `_generate_recommendations` 方法
- **状态**: 待修复
- **验证**: 测试火车超标时是否同时推荐符合差标的机票

### TODO-004: Hotel Agent 超标双重推荐逻辑不完整
- **文件**: `backend/app/agents/hotel.py`
- **问题**: 用户期望豪华酒店超标时，未生成符合预算的豪华酒店替代推荐
- **位置**: `reasoning_decision_layer` 方法，第169-185行
- **状态**: 待修复
- **验证**: 测试超标时是否同时给出合规推荐和替代推荐

## P1 优先级（功能增强）

### TODO-005: Dispatcher Agent 多Agent协作不完整
- **文件**: `backend/app/agents/dispatcher.py`
- **问题**: 仅创建工作流，未实现真正的任务分发和结果聚合
- **状态**: 待修复
- **验证**: 测试多Agent是否真正并行协作

### TODO-006: Invoice Agent OCR服务未接入
- **文件**: `backend/app/services/invoice_ocr.py`
- **问题**: 只有Mock实现，未接入真实OCR服务
- **状态**: 待修复
- **验证**: 测试上传发票图片是否能正确识别

### TODO-007: Mock Data Agent web-content-fetcher未集成
- **文件**: `backend/app/agents/mock_data.py`
- **问题**: 配置了skill路径但未真正调用
- **状态**: 待修复
- **验证**: 测试是否能获取真实数据并生成Mock

## P2 优先级（体验优化）

### TODO-008: 移除正则降级方案
- **文件**: `backend/app/agents/intent.py`
- **问题**: 使用正则作为LLM解析失败时的降级方案
- **状态**: 待修复
- **验证**: 确保所有解析都通过LLM语义理解

### TODO-009: 对话上下文管理增强
- **文件**: `backend/app/services/session_manager.py`
- **问题**: 多轮对话状态追踪不够完善
- **状态**: 待优化
- **验证**: 测试多轮对话是否正确追踪上下文

---

## 测试计划

每次修复完成后，必须执行以下测试：

### 测试1: 流式响应测试
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "我明天从北京去上海出差"}'
```
预期：消息只显示一次，不重复

### 测试2: 追问完整性测试
输入： "我明天要去深圳出差"
预期：AI追问所有缺失字段（职级、出行方式、住宿、宴请等）

### 测试3: 火车超标推荐测试
输入：提供火车选择但火车价格超标
预期：同时推荐符合差标的机票选项

### 测试4: 酒店超标推荐测试
输入：基层员工期望住五星级酒店
预期：告知超标，并给出合规推荐和替代推荐

### 测试5: 审批单生成测试
输入：完成所有选择后
预期：成功生成审批单

---

## 当前状态

- [ ] TODO-001: 前端消息重复
- [ ] TODO-002: Intent追问不完整
- [ ] TODO-003: 火车超标未推荐机票
- [ ] TODO-004: 酒店超标推荐不完整
- [ ] TODO-005: 多Agent协作
- [ ] TODO-006: 发票OCR
- [ ] TODO-007: Mock Data集成
- [ ] TODO-008: 移除正则降级
- [ ] TODO-009: 上下文管理
