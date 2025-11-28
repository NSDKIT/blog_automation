-- ============================================
-- articles テーブルのstatusカラムのデフォルト値を修正
-- ============================================
-- 
-- 問題: statusのデフォルト値が'draft'になっているため、
-- 明示的に設定しない場合に'draft'になってしまう可能性がある
--
-- 解決策: デフォルト値を'keyword_analysis'に変更
-- ============================================

-- 現在のデフォルト値を確認
SELECT 
    column_name, 
    column_default, 
    data_type
FROM information_schema.columns
WHERE table_name = 'articles' 
AND column_name = 'status';

-- デフォルト値を'keyword_analysis'に変更
ALTER TABLE articles 
ALTER COLUMN status SET DEFAULT 'keyword_analysis';

-- 変更を確認
SELECT 
    column_name, 
    column_default, 
    data_type
FROM information_schema.columns
WHERE table_name = 'articles' 
AND column_name = 'status';

-- 完了メッセージ
DO $$
BEGIN
    RAISE NOTICE 'articlesテーブルのstatusカラムのデフォルト値をkeyword_analysisに変更しました。';
END $$;

