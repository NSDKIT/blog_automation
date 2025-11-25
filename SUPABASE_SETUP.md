# Supabaseセットアップガイド

## 1. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com)にアクセス
2. 新しいプロジェクトを作成
3. プロジェクトのURLとAPIキーを取得

## 2. 環境変数の設定

`.env`ファイルに以下を追加：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

## 3. テーブルの作成

SupabaseダッシュボードのSQL Editorで以下を実行：

### knowledge_base テーブル

```sql
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

-- RLS (Row Level Security) を有効化
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能
CREATE POLICY "knowledge_base_select" ON knowledge_base
  FOR SELECT USING (true);
```

### images テーブル

```sql
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

-- RLS を有効化
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能
CREATE POLICY "images_select" ON images
  FOR SELECT USING (true);
```

## 4. サンプルデータの投入

### 知識ベースデータ

```sql
INSERT INTO knowledge_base (title, content, keywords) VALUES
('眼鏡生産者の想い', '私たちは職人の技術を大切にし、お客様に最高の眼鏡をお届けします。', ARRAY['職人技術', '眼鏡', '品質']),
('ブルーライトカットの重要性', 'デジタルデバイスの使用が増える現代において、ブルーライトカットは目の健康に重要です。', ARRAY['ブルーライトカット', '健康', 'デジタル']);
```

### 画像データ

```sql
INSERT INTO images (url, alt_text, category, keywords) VALUES
('https://example.com/image1.jpg', '眼鏡の画像1', '1n908lNr3Pum1BrcSyvxfyCJgiYG-KAhOreJszJHHYJw', ARRAY['眼鏡', 'メガネ']),
('https://example.com/image2.jpg', '眼鏡の画像2', '1n908lNr3Pum1BrcSyvxfyCJgiYG-KAhOreJszJHHYJw', ARRAY['眼鏡', 'ブルーライト']);
```

## 5. 日本語全文検索の有効化（オプション）

日本語全文検索を使用する場合：

```sql
-- pg_trgm拡張を有効化
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 日本語用のインデックス
CREATE INDEX idx_knowledge_base_content_trgm ON knowledge_base USING gin(content gin_trgm_ops);
```

