-- ============================================
-- articles テーブルの実用的なRLSポリシー
-- ============================================
-- 
-- このスクリプトは、カスタム認証を使用するアプリケーション向けの
-- 実用的なRLSポリシーを提供します。
--
-- アプローチ1: Service Role Keyを使用する場合（推奨）
--   - RLSを無効化するか、すべて許可するポリシー
--   - アプリケーション層で完全に制御
--
-- アプローチ2: Anon Keyを使用する場合
--   - カスタム関数を使用してuser_idを検証
--   - より安全だが、実装が複雑
-- ============================================

-- ============================================
-- アプローチ1: Service Role Keyを使用する場合（推奨）
-- ============================================
-- このアプローチでは、Service Role Keyを使用し、
-- アプリケーション層でuser_idによるフィルタリングを実装します。
-- RLSは防御の一層として機能しますが、基本的にはバイパスされます。

-- RLSを有効化
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 既存のポリシーを削除
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;

-- Service Role Keyを使用している場合、RLSはバイパスされますが、
-- 念のため、すべての操作を許可するポリシーを設定します。
-- 実際のセキュリティは、アプリケーション層で実装されています。

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
-- アプローチ2: Anon Keyを使用する場合（上級者向け）
-- ============================================
-- このアプローチでは、Anon Keyを使用し、
-- PostgreSQL関数を使用してuser_idを検証します。
-- 
-- 注意: このアプローチを使用する場合は、上記のポリシーを削除してから
-- 以下のポリシーを適用してください。

/*
-- 既存のポリシーを削除
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;

-- user_idを検証する関数
-- この関数は、リクエストヘッダーやセッション変数からuser_idを取得します
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
DECLARE
    user_id_text TEXT;
BEGIN
    -- 方法1: セッション変数から取得（アプリケーション層で設定）
    user_id_text := current_setting('app.current_user_id', true);
    
    -- 方法2: JWTクレームから取得（Supabase Authを使用している場合）
    -- user_id_text := (current_setting('request.jwt.claims', true)::json->>'sub');
    
    IF user_id_text IS NULL OR user_id_text = '' THEN
        RETURN NULL;
    END IF;
    
    RETURN user_id_text::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- SELECT ポリシー
CREATE POLICY "articles_select_own" ON articles
    FOR SELECT
    USING (get_current_user_id() = user_id);

-- INSERT ポリシー
CREATE POLICY "articles_insert_own" ON articles
    FOR INSERT
    WITH CHECK (get_current_user_id() = user_id);

-- UPDATE ポリシー
CREATE POLICY "articles_update_own" ON articles
    FOR UPDATE
    USING (get_current_user_id() = user_id)
    WITH CHECK (get_current_user_id() = user_id);

-- DELETE ポリシー
CREATE POLICY "articles_delete_own" ON articles
    FOR DELETE
    USING (get_current_user_id() = user_id);
*/

-- ============================================
-- アプローチ3: RLSを完全に無効化（開発環境のみ）
-- ============================================
-- 開発環境でRLSを完全に無効化したい場合:
-- ALTER TABLE articles DISABLE ROW LEVEL SECURITY;

-- ============================================
-- ポリシーの確認
-- ============================================
-- 以下のクエリで、設定されたポリシーを確認できます:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies
-- WHERE tablename = 'articles';

-- ============================================
-- 推奨事項
-- ============================================
-- 1. **アプローチ1（Service Role Key）を推奨**
--    - シンプルで実装が容易
--    - アプリケーション層で完全に制御可能
--    - 現在のコードベースと互換性が高い
--
-- 2. **セキュリティの多層防御**
--    - RLSは防御の一層として機能
--    - アプリケーション層でもuser_idによるフィルタリングを実装
--    - バックエンドAPIで認証・認可を実装
--
-- 3. **Service Role Keyの管理**
--    - 環境変数で管理
--    - 本番環境では厳重に管理
--    - ログに出力しない
--
-- 4. **監査ログ**
--    - すべての操作をaudit_logsテーブルに記録
--    - 異常なアクセスを検出可能

