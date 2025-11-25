"""
Supabaseテーブル用のモデル定義（参考用）
実際のテーブルはSupabaseダッシュボードで作成してください
"""

# knowledge_base テーブル
"""
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  keywords TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 全文検索用のインデックス
CREATE INDEX idx_knowledge_base_content ON knowledge_base USING gin(to_tsvector('japanese', content));
CREATE INDEX idx_knowledge_base_keywords ON knowledge_base USING gin(keywords);
"""

# images テーブル
"""
CREATE TABLE images (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  url TEXT NOT NULL,
  alt_text TEXT,
  category TEXT,
  keywords TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_images_category ON images(category);
CREATE INDEX idx_images_keywords ON images USING gin(keywords);
"""

