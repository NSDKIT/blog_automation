# articlesテーブルのRLSポリシー設定ガイド

このガイドでは、カスタム認証を使用するアプリケーション向けの理想的なRLSポリシーの設定方法を説明します。

## 📋 目次

1. [概要](#概要)
2. [アプローチの選択](#アプローチの選択)
3. [設定手順](#設定手順)
4. [セキュリティの考慮事項](#セキュリティの考慮事項)
5. [トラブルシューティング](#トラブルシューティング)

## 概要

このアプリケーションは、カスタム認証（JWTトークン）を使用しており、Supabaseの標準的な`auth.uid()`は使用できません。そのため、以下の2つのアプローチから選択できます：

### アプローチ1: Service Role Keyを使用（推奨）

- **特徴**: シンプルで実装が容易
- **RLS**: 基本的にバイパスされるが、防御の一層として機能
- **セキュリティ**: アプリケーション層で完全に制御
- **推奨**: 現在のコードベースに最適

### アプローチ2: Anon Keyを使用（上級者向け）

- **特徴**: より厳格なセキュリティ
- **RLS**: データベース層で強制
- **セキュリティ**: データベース層とアプリケーション層の両方で制御
- **注意**: 実装が複雑で、カスタム関数が必要

## アプローチの選択

### 現在のコードベースの確認

```python
# backend/app/supabase_client.py
SUPABASE_RLS_MODE = os.getenv("SUPABASE_RLS_MODE", "service").lower()
```

- **デフォルト**: `"service"` (Service Role Keyを使用)
- **推奨**: アプローチ1を使用

## 設定手順

### ステップ1: 既存のポリシーを確認

SupabaseダッシュボードのSQL Editorで以下を実行：

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'articles';
```

### ステップ2: 新しいポリシーを適用

#### アプローチ1: Service Role Keyを使用（推奨）

`backend/articles_rls_policy_practical.sql` の **アプローチ1** を実行：

```sql
-- RLSを有効化
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 既存のポリシーを削除
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;

-- 新しいポリシーを作成
CREATE POLICY "articles_select_own" ON articles
    FOR SELECT USING (true);

CREATE POLICY "articles_insert_own" ON articles
    FOR INSERT WITH CHECK (true);

CREATE POLICY "articles_update_own" ON articles
    FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "articles_delete_own" ON articles
    FOR DELETE USING (true);
```

#### アプローチ2: Anon Keyを使用（上級者向け）

`backend/articles_rls_policy_practical.sql` の **アプローチ2** のコメントを外して実行。

**注意**: このアプローチを使用する場合は、アプリケーション層でセッション変数を設定する必要があります。

### ステップ3: ポリシーの確認

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename = 'articles';
```

## セキュリティの考慮事項

### 多層防御の実装

RLSは防御の一層として機能しますが、アプリケーション層でもセキュリティを実装してください：

#### 1. バックエンドAPIでの認証・認可

```python
# backend/app/routers/articles.py
@router.get("/{article_id}")
async def get_article(
    article_id: UUID,
    current_user: dict = Depends(get_current_user)  # 認証必須
):
    # user_idによるフィルタリング
    article = get_article_by_id(str(article_id), str(current_user.get("id")))
    if not article:
        raise HTTPException(status_code=404, detail="記事が見つかりません")
    return article
```

#### 2. データベースクエリでのuser_idフィルタリング

```python
# backend/app/supabase_db.py
def get_article_by_id(article_id: str, user_id: str) -> Optional[Dict]:
    response = supabase.table("articles")\
        .select("*")\
        .eq("id", article_id)\
        .eq("user_id", user_id)  # user_idでフィルタリング
        .limit(1)\
        .execute()
```

#### 3. Service Role Keyの管理

- ✅ 環境変数で管理
- ✅ `.env`ファイルに追加（`.gitignore`に含める）
- ❌ コードにハードコードしない
- ❌ ログに出力しない
- ❌ クライアント側に公開しない

### 監査ログ

すべての操作を`audit_logs`テーブルに記録：

```python
# backend/app/routers/articles.py
create_audit_log(
    user_id=str(current_user.get("id")),
    action="article_created",
    metadata={"article_id": article.get("id")},
    ip_address=get_client_ip(request)
)
```

## トラブルシューティング

### 問題1: RLSポリシーが適用されない

**原因**: Service Role Keyを使用している場合、RLSはバイパスされます。

**解決策**: これは正常な動作です。アプリケーション層でuser_idによるフィルタリングを実装してください。

### 問題2: 記事にアクセスできない

**原因**: 
- Anon Keyを使用している場合、RLSポリシーが適用されている
- JWTトークンにuser_idが含まれていない

**解決策**:
1. Service Role Keyを使用しているか確認
2. アプリケーション層でuser_idによるフィルタリングを実装
3. 認証トークンが正しく設定されているか確認

### 問題3: ポリシーの削除

```sql
-- すべてのポリシーを削除
DROP POLICY IF EXISTS "articles_select_own" ON articles;
DROP POLICY IF EXISTS "articles_insert_own" ON articles;
DROP POLICY IF EXISTS "articles_update_own" ON articles;
DROP POLICY IF EXISTS "articles_delete_own" ON articles;

-- RLSを無効化（開発環境のみ）
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;
```

### 問題4: パフォーマンスの問題

**原因**: RLSポリシーが複雑な場合、クエリのパフォーマンスに影響する可能性があります。

**解決策**:
- インデックスを確認: `CREATE INDEX IF NOT EXISTS idx_articles_user_id ON articles(user_id);`
- ポリシーをシンプルに保つ
- Service Role Keyを使用する場合は、RLSの影響は最小限

## 推奨設定

### 本番環境

```sql
-- アプローチ1を使用（Service Role Key）
-- backend/articles_rls_policy_practical.sql のアプローチ1を適用

-- 追加のセキュリティ対策:
-- 1. アプリケーション層でuser_idによるフィルタリング
-- 2. すべての操作をaudit_logsに記録
-- 3. Service Role Keyを環境変数で管理
-- 4. 定期的にアクセスログを監査
```

### 開発環境

```sql
-- 開発環境では、RLSを無効化することも可能
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;

-- ただし、本番環境と同じ設定を推奨
```

## 参考資料

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [backend/app/supabase_client.py](../backend/app/supabase_client.py)
- [backend/app/routers/articles.py](../backend/app/routers/articles.py)

