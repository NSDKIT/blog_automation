-- ============================================
-- articles テーブルのトリガーと制約を確認
-- ============================================
-- 
-- statusがprocessingになる原因を特定するための診断スクリプト
-- ============================================

-- 1. テーブルのデフォルト値を確認
SELECT 
    column_name, 
    column_default, 
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'articles' 
AND column_name = 'status';

-- 2. トリガーを確認
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'articles'
ORDER BY trigger_name;

-- 3. 制約を確認
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'articles'::regclass
ORDER BY conname;

-- 4. RLSポリシーを確認
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

-- 5. 最近作成された記事のstatusを確認（デバッグ用）
SELECT 
    id,
    user_id,
    keyword,
    status,
    created_at,
    updated_at
FROM articles
ORDER BY created_at DESC
LIMIT 5;

-- 6. statusの値の分布を確認
SELECT 
    status,
    COUNT(*) as count
FROM articles
GROUP BY status
ORDER BY count DESC;

