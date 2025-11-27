-- キーワード分析機能用のカラムを追加
-- SupabaseダッシュボードのSQL Editorで実行してください

-- キーワード分析関連のカラムを追加
ALTER TABLE articles ADD COLUMN IF NOT EXISTS analyzed_keywords JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS selected_keywords JSONB;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS selected_keywords_data JSONB;

-- カラムが追加されたことを確認
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'articles' 
AND column_name IN ('analyzed_keywords', 'selected_keywords', 'selected_keywords_data');

