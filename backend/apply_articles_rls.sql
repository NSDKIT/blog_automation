-- ============================================
-- articles テーブルのRLSポリシー適用スクリプト
-- ============================================
-- 
-- このスクリプトは、Service Role Keyを使用するアプリケーション向けの
-- 実用的なRLSポリシーを適用します。
--
-- 使用方法:
-- 1. SupabaseダッシュボードのSQL Editorで実行
-- 2. または、psqlコマンドで実行: psql -f apply_articles_rls.sql
--
-- 注意:
-- - このスクリプトは既存のポリシーを削除してから新しいポリシーを作成します
-- - 本番環境で実行する前に、必ずバックアップを取得してください
-- ============================================

-- ============================================
-- 1. RLSを有効化
-- ============================================
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 2. 既存のポリシーを削除
-- ============================================
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;

-- ============================================
-- 3. 新しいポリシーを作成
-- ============================================

-- SELECT ポリシー（読み取り）
-- アプリケーション層でuser_idによるフィルタリングが実装されているため、
-- ここではすべての記事を許可します。
CREATE POLICY "articles_select_own" ON articles
    FOR SELECT
    USING (true);

-- INSERT ポリシー（作成）
-- アプリケーション層でuser_idが設定されているため、
-- ここではすべての作成を許可します。
CREATE POLICY "articles_insert_own" ON articles
    FOR INSERT
    WITH CHECK (true);

-- UPDATE ポリシー（更新）
-- アプリケーション層でuser_idによる検証が実装されているため、
-- ここではすべての更新を許可します。
CREATE POLICY "articles_update_own" ON articles
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- DELETE ポリシー（削除）
-- アプリケーション層でuser_idによる検証が実装されているため、
-- ここではすべての削除を許可します。
CREATE POLICY "articles_delete_own" ON articles
    FOR DELETE
    USING (true);

-- ============================================
-- 4. ポリシーの確認
-- ============================================
-- 以下のクエリで、設定されたポリシーを確認できます:
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    permissive, 
    roles, 
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'articles'
ORDER BY policyname;

-- ============================================
-- 5. インデックスの確認（パフォーマンス向上のため）
-- ============================================
-- user_idによるフィルタリングが頻繁に行われるため、
-- インデックスが存在することを確認してください
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'articles' 
AND indexname LIKE '%user_id%';

-- インデックスが存在しない場合は、以下を実行:
-- CREATE INDEX IF NOT EXISTS idx_articles_user_id ON articles(user_id);

-- ============================================
-- 完了メッセージ
-- ============================================
DO $$
BEGIN
    RAISE NOTICE 'articlesテーブルのRLSポリシーが正常に適用されました。';
    RAISE NOTICE 'アプリケーション層でuser_idによるフィルタリングが実装されていることを確認してください。';
END $$;

