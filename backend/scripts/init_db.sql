-- 智能商旅助手数据库初始化脚本
-- Supabase PostgreSQL

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    user_level TEXT DEFAULT '基层员工',
    department TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 出差记录表
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    employee_name TEXT,
    user_level TEXT,
    department TEXT,
    purpose TEXT,
    departure TEXT,
    destination TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'pending',
    total_cost DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 预订记录表
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    user_id UUID REFERENCES users(id),
    booking_type TEXT NOT NULL,
    provider TEXT,
    booking_ref TEXT,
    status TEXT DEFAULT 'pending',
    amount DECIMAL(10, 2),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 审批单表
CREATE TABLE IF NOT EXISTS approval_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    user_id UUID REFERENCES users(id),
    form_data JSONB,
    approval_status TEXT DEFAULT 'pending',
    approval_chain JSONB,
    total_amount DECIMAL(10, 2),
    needs_special_approval BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 发票表
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES trips(id),
    user_id UUID REFERENCES users(id),
    invoice_type TEXT,
    invoice_code TEXT,
    invoice_number TEXT,
    invoice_date DATE,
    buyer_name TEXT,
    seller_name TEXT,
    amount DECIMAL(10, 2),
    tax_rate TEXT,
    details JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. 对话记录表
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id TEXT UNIQUE,
    context JSONB,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. 消息记录表
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    role TEXT NOT NULL,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. 索引
CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);
CREATE INDEX IF NOT EXISTS idx_bookings_trip_id ON bookings(trip_id);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_approval_forms_trip_id ON approval_forms(trip_id);
CREATE INDEX IF NOT EXISTS idx_invoices_trip_id ON invoices(trip_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- 9. RLS 策略 (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 基础策略：用户只能访问自己的数据
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own trips" ON trips FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can insert own trips" ON trips FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can update own trips" ON trips FOR UPDATE USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));

CREATE POLICY "Users can view own bookings" ON bookings FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can insert own bookings" ON bookings FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid() = id));

CREATE POLICY "Users can view own approval forms" ON approval_forms FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can insert own approval forms" ON approval_forms FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid() = id));

CREATE POLICY "Users can view own invoices" ON invoices FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can insert own invoices" ON invoices FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid() = id));

CREATE POLICY "Users can view own conversations" ON conversations FOR SELECT USING (user_id = (SELECT id FROM users WHERE auth.uid() = id));
CREATE POLICY "Users can insert own conversations" ON conversations FOR INSERT WITH CHECK (user_id = (SELECT id FROM users WHERE auth.uid() = id));

CREATE POLICY "Users can view own messages" ON messages FOR SELECT USING (conversation_id IN (SELECT id FROM conversations WHERE user_id = (SELECT id FROM users WHERE auth.uid() = id)));
CREATE POLICY "Users can insert own messages" ON messages FOR INSERT WITH CHECK (conversation_id IN (SELECT id FROM conversations WHERE user_id = (SELECT id FROM users WHERE auth.uid() = id)));