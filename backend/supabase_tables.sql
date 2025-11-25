-- Supabaseでアプリケーション用のテーブルを作成するSQLスクリプト
-- SupabaseダッシュボードのSQL Editorで実行してください

-- UUID拡張を有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pg_trgm拡張を有効化（全文検索用）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================
-- 1. users テーブル（ユーザー管理）
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- updated_atを自動更新するトリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 2. articles テーブル（記事管理）
-- ============================================
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    target VARCHAR(255) NOT NULL,
    article_type VARCHAR(255) NOT NULL,
    title TEXT,
    content TEXT,
    shopify_article_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_articles_user_id ON articles(user_id);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);

-- updated_atを自動更新するトリガー
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 3. article_histories テーブル（記事履歴）
-- ============================================
CREATE TABLE IF NOT EXISTS article_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    changes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_article_histories_article_id ON article_histories(article_id);
CREATE INDEX IF NOT EXISTS idx_article_histories_created_at ON article_histories(created_at DESC);

-- ============================================
-- 4. settings テーブル（設定管理）
-- ============================================
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);

-- updated_atを自動更新するトリガー
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. knowledge_base テーブル（知識ベース）
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_knowledge_base_keywords ON knowledge_base USING gin(keywords);
-- 全文検索インデックス（日本語設定がない場合はデフォルトを使用）
-- 日本語全文検索が必要な場合は、pg_trgm拡張を使用する方法に変更
CREATE INDEX IF NOT EXISTS idx_knowledge_base_content_trgm ON knowledge_base USING gin(content gin_trgm_ops);

-- updated_atを自動更新するトリガー
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 6. images テーブル（画像管理）
-- ============================================
CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    alt_text TEXT,
    category TEXT,
    keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_images_category ON images(category);
CREATE INDEX IF NOT EXISTS idx_images_keywords ON images USING gin(keywords);

-- ============================================
-- Row Level Security (RLS) の設定
-- ============================================

-- users テーブル
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能（認証済みユーザーのみ）
CREATE POLICY "users_select" ON users
    FOR SELECT USING (true);

-- 全ユーザーが新規作成可能
CREATE POLICY "users_insert" ON users
    FOR INSERT WITH CHECK (true);

-- 自分のデータのみ更新可能
CREATE POLICY "users_update_own" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- articles テーブル
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 自分の記事のみ読み取り可能
CREATE POLICY "articles_select_own" ON articles
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- 自分の記事のみ作成可能
CREATE POLICY "articles_insert_own" ON articles
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- 自分の記事のみ更新可能
CREATE POLICY "articles_update_own" ON articles
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- 自分の記事のみ削除可能
CREATE POLICY "articles_delete_own" ON articles
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- article_histories テーブル
ALTER TABLE article_histories ENABLE ROW LEVEL SECURITY;

-- 自分の記事の履歴のみ読み取り可能
CREATE POLICY "article_histories_select_own" ON article_histories
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM articles
            WHERE articles.id = article_histories.article_id
            AND articles.user_id::text = auth.uid()::text
        )
    );

-- settings テーブル
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- 自分の設定のみ読み取り可能
CREATE POLICY "settings_select_own" ON settings
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- 自分の設定のみ作成・更新可能
CREATE POLICY "settings_insert_own" ON settings
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "settings_update_own" ON settings
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- knowledge_base テーブル（全ユーザーが読み取り可能）
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

CREATE POLICY "knowledge_base_select" ON knowledge_base
    FOR SELECT USING (true);

-- images テーブル（全ユーザーが読み取り可能）
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "images_select" ON images
    FOR SELECT USING (true);

-- ============================================
-- サンプルデータの投入（オプション）
-- ============================================

-- 知識ベースのサンプルデータ
INSERT INTO knowledge_base (title, content, keywords) VALUES
('眼鏡生産者の想い', '私たちは職人の技術を大切にし、お客様に最高の眼鏡をお届けします。鯖江の伝統技術と最新の素材を組み合わせ、快適性とデザイン性を両立させた眼鏡を作り続けています。', ARRAY['職人技術', '眼鏡', '品質', '鯖江']),
('ブルーライトカットの重要性', 'デジタルデバイスの使用が増える現代において、ブルーライトカットは目の健康に重要です。長時間のPC作業やゲーム、スマートフォンの使用で目が疲れやすい方に特におすすめです。', ARRAY['ブルーライトカット', '健康', 'デジタル', 'PC作業']),
('βチタニウムの特徴', 'βチタニウムは軽量で丈夫、そして柔軟性に優れた素材です。長時間の着用でも疲れにくく、顔に優しくフィットします。スポーツやアクティブなライフスタイルにも最適です。', ARRAY['βチタニウム', '軽量', '耐久性', '快適性']),
('インドアライフと眼鏡', 'リモートワークやゲーム、クリエイティブワークなど、インドアでの活動が増えています。適切な眼鏡選びは、生産性と快適性を大きく向上させます。', ARRAY['インドアライフ', 'リモートワーク', 'ゲーム', 'クリエイティブ']),
('EIGHTOONのこだわり', 'EIGHTOONは、インドアライフを楽しむ方々のために、機能性とデザイン性を兼ね備えた眼鏡を提供しています。職人の技術と最新の素材を組み合わせ、快適な視生活をサポートします。', ARRAY['EIGHTOON', 'インドアライフ', '職人技術', '快適性'])
ON CONFLICT DO NOTHING;

-- 画像のサンプルデータ（実際のURLに置き換えてください）
INSERT INTO images (url, alt_text, category, keywords) VALUES
('https://example.com/glasses1.jpg', '眼鏡の画像1', '1n908lNr3Pum1BrcSyvxfyCJgiYG-KAhOreJszJHHYJw', ARRAY['眼鏡', 'メガネ']),
('https://example.com/glasses2.jpg', '眼鏡の画像2', '1n908lNr3Pum1BrcSyvxfyCJgiYG-KAhOreJszJHHYJw', ARRAY['眼鏡', 'ブルーライト']),
('https://example.com/glasses3.jpg', '眼鏡の画像3', '1n908lNr3Pum1BrcSyvxfyCJgiYG-KAhOreJszJHHYJw', ARRAY['眼鏡', 'ゲーミング'])
ON CONFLICT DO NOTHING;

