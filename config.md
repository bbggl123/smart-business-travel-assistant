# 智能商旅助手 - 项目配置

## ⚠️ 重要提示
此文件包含敏感信息，请勿提交到版本控制系统！
请将此文件加入 .gitignore

---

## API Keys & 凭证

### 紫东太初 (Zidongtaichu)
- API端点: `https://cloud.zidongtaichu.com/maas/v1/chat/completions`
- API Key: `z0oxh3h9tbeq2gihnvdhq0el`
- 模型: `Kimi-K2.5`
- 调用方式: REST API (stream: true)
- 用途: LLM推理、多模态发票识别

### 高德地图 (AMap)
- Web端API Key: `8d1fd7a0ea3fbd4053e853cefac9d175`
- 用途: POI搜索、地理编码、距离计算

### Supabase
- 项目名称: `bbggdllll21@2925.com's Project`
- 项目密码: `970801Lqzhi.com`
- 用途: PostgreSQL数据库、Redis缓存、会话存储

### KittenTTS
- GitHub: `https://github.com/KittenML/KittenTTS`
- 用途: 文字转语音 (TTS)

---

## 环境变量配置示例 (.env.example)

```bash
# 紫东太初 LLM
ZIDONGTAICHU_API_KEY=z0oxh3h9tbeq2gihnvdhq0el
ZIDONGTAICHU_API_URL=https://cloud.zidongtaichu.com/maas/v1/chat/completions
ZIDONGTAICHU_MODEL=Kimi-K2.5

# 高德地图
AMAP_API_KEY=8d1fd7a0ea3fbd4053e853cefac9d175

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis (如本地部署)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 后端服务
BACKEND_URL=http://localhost:8000
WS_URL=ws://localhost:8000
```

---

## 服务连接配置

### 后端 API (FastAPI)
- 本地开发: `http://localhost:8000`
- 生产环境: (待配置)

### WebSocket
- 本地开发: `ws://localhost:8000/ws`
- 生产环境: (待配置)

### Supabase
- PostgreSQL: `postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres`
- Redis: `redis://default:[PASSWORD]@[PROJECT_ID].supabase.co:6379`

---

## 功能开关配置

```typescript
// src/config/features.ts
export const featureFlags = {
  // 语音交互 (需要KittenTTS部署)
  voiceEnabled: true,

  // 发票识别 (需要紫东太初多模态)
  invoiceOcrEnabled: true,

  // 真实数据获取 (需要高德API)
  realDataEnabled: true,

  // Mock模式 (不调用真实API)
  mockMode: process.env.NODE_ENV === 'development',

  // COT展示模式 (调试用)
  cotDebugMode: process.env.NODE_ENV === 'development',
};
```

---

**版本**: v1.0
**更新日期**: 2026-03-22