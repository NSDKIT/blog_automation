-- ============================================
-- articles テーブルの理想的なRLSポリシー
-- ============================================
-- 
-- このスクリプトは、カスタム認証を使用するアプリケーション向けの
-- 理想的なRLSポリシーを提供します。
--
-- 使用方法:
-- 1. SupabaseダッシュボードのSQL Editorで実行
-- 2. または、psqlコマンドで実行
--
-- 注意:
-- - Service Role Keyを使用する場合: RLSはバイパスされます（すべて許可）
-- - Anon Keyを使用する場合: RLSが適用されます
-- - カスタム認証を使用しているため、auth.uid()の代わりにJWTクレームを使用
-- ============================================

-- ============================================
-- 1. RLSを有効化
-- ============================================
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 2. 既存のポリシーを削除（再作成する場合）
-- ============================================
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;
DROP POLICY IF EXISTS "articles_select_by_user_id" ON articles;
DROP POLICY IF EXISTS "articles_service_role_bypass" ON articles;

-- ============================================
-- 3. JWTクレームからuser_idを取得する関数
-- ============================================
-- カスタム認証を使用している場合、JWTトークンの'sub'クレームにuser_idが含まれます
-- この関数は、JWTクレームからuser_idを取得します
CREATE OR REPLACE FUNCTION get_user_id_from_jwt()
RETURNS UUID AS $$
BEGIN
    -- JWTクレームから'sub'（user_id）を取得
    -- カスタム認証の場合、'sub'にuser_idが含まれていることを想定
    RETURN (current_setting('request.jwt.claims', true)::json->>'sub')::UUID;
EXCEPTION
    WHEN OTHERS THEN
        -- JWTクレームが取得できない場合（Service Role Key使用時など）
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ============================================
-- 4. SELECT ポリシー（読み取り）
-- ============================================
-- 自分の記事のみ読み取り可能
-- Service Role Keyを使用している場合は、このポリシーはバイパスされます
CREATE POLICY "articles_select_own" ON articles
    FOR SELECT
    USING (
        -- JWTクレームからuser_idを取得して比較
        get_user_id_from_jwt() = user_id
        OR
        -- Service Role Keyを使用している場合（JWTクレームがNULL）
        get_user_id_from_jwt() IS NULL
    );

-- ============================================
-- 5. INSERT ポリシー（作成）
-- ============================================
-- 自分のuser_idで記事を作成可能
-- Service Role Keyを使用している場合は、このポリシーはバイパスされます
CREATE POLICY "articles_insert_own" ON articles
    FOR INSERT
    WITH CHECK (
        -- 作成しようとしているuser_idが、JWTクレームのuser_idと一致
        get_user_id_from_jwt() = user_id
        OR
        -- Service Role Keyを使用している場合（JWTクレームがNULL）
        get_user_id_from_jwt() IS NULL
    );

-- ============================================
-- 6. UPDATE ポリシー（更新）
-- ============================================
-- 自分の記事のみ更新可能
-- Service Role Keyを使用している場合は、このポリシーはバイパスされます
CREATE POLICY "articles_update_own" ON articles
    FOR UPDATE
    USING (
        -- 既存の記事のuser_idが、JWTクレームのuser_idと一致
        get_user_id_from_jwt() = user_id
        OR
        -- Service Role Keyを使用している場合（JWTクレームがNULL）
        get_user_id_from_jwt() IS NULL
    )
    WITH CHECK (
        -- 更新後のuser_idも、JWTクレームのuser_idと一致（user_idの変更を防ぐ）
        get_user_id_from_jwt() = user_id
        OR
        -- Service Role Keyを使用している場合（JWTクレームがNULL）
        get_user_id_from_jwt() IS NULL
    );

-- ============================================
-- 7. DELETE ポリシー（削除）
-- ============================================
-- 自分の記事のみ削除可能
-- Service Role Keyを使用している場合は、このポリシーはバイパスされます
CREATE POLICY "articles_delete_own" ON articles
    FOR DELETE
    USING (
        -- 削除しようとしている記事のuser_idが、JWTクレームのuser_idと一致
        get_user_id_from_jwt() = user_id
        OR
        -- Service Role Keyを使用している場合（JWTクレームがNULL）
        get_user_id_from_jwt() IS NULL
    );

-- ============================================
-- 8. 代替案: Service Role Key用の明示的なバイパスポリシー
-- ============================================
-- 上記のポリシーで `get_user_id_from_jwt() IS NULL` をチェックしていますが、
-- より明示的にService Role Keyをバイパスしたい場合は、以下のポリシーを使用できます。
-- 
-- 注意: このポリシーは、Service Role Keyを使用している場合にのみ有効です。
-- Anon Keyを使用している場合は、上記のポリシーが適用されます。
--
-- CREATE POLICY "articles_service_role_bypass" ON articles
--     FOR ALL
--     USING (true)
--     WITH CHECK (true);

-- ============================================
-- 9. ポリシーの確認
-- ============================================
-- 以下のクエリで、設定されたポリシーを確認できます:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies
-- WHERE tablename = 'articles';

-- ============================================
-- 10. テスト用のクエリ（開発環境のみ）
-- ============================================
-- 以下のクエリで、JWTクレームからuser_idを取得できるかテストできます:
-- SELECT get_user_id_from_jwt();

-- ============================================
-- 注意事項
-- ============================================
-- 1. Service Role Keyを使用している場合:
--    - RLSポリシーはバイパスされます（すべての操作が許可されます）
--    - アプリケーション層でuser_idによるフィルタリングを実装してください
--
-- 2. Anon Keyを使用している場合:
--    - RLSポリシーが適用されます
--    - JWTトークンに'sub'クレームが含まれている必要があります
--
-- 3. カスタム認証を使用している場合:
--    - Supabaseのauth.uid()は使用できません
--    - 代わりに、JWTクレームからuser_idを取得する必要があります
--
-- 4. セキュリティ:
--    - アプリケーション層でもuser_idによるフィルタリングを実装してください
--    - RLSは防御の一層として機能します
--    - Service Role Keyは機密情報として扱い、環境変数で管理してください

