# statusがprocessingになる問題の診断と解決方法

## 問題

「記事を生成」ボタンを押すと、`status`が`processing`になってしまう。

## 診断手順

### 1. サーバーログを確認

以下のログを確認してください：

```
[create_article] 記事作成開始: status=keyword_analysis
[create_article] 送信するstatus値: 'keyword_analysis'
[create_article] 生データのstatus: '...'
[create_article] データベースから直接確認: status='...'
[create_article_endpoint] 最終レスポンス: status=...
```

### 2. データベースの状態を確認

SupabaseダッシュボードのSQL Editorで以下を実行：

```sql
-- backend/check_articles_triggers.sql を実行
```

確認項目：
- `status`カラムのデフォルト値
- トリガーの有無
- 制約の有無
- RLSポリシーの設定

### 3. 最近作成された記事を確認

```sql
SELECT 
    id,
    keyword,
    status,
    created_at,
    updated_at
FROM articles
ORDER BY created_at DESC
LIMIT 5;
```

## 考えられる原因

### 1. データベースのデフォルト値

**確認方法:**
```sql
SELECT column_default 
FROM information_schema.columns
WHERE table_name = 'articles' 
AND column_name = 'status';
```

**解決方法:**
```sql
ALTER TABLE articles 
ALTER COLUMN status SET DEFAULT 'keyword_analysis';
```

### 2. データベースのトリガー

**確認方法:**
```sql
SELECT trigger_name, action_statement
FROM information_schema.triggers
WHERE event_object_table = 'articles';
```

**解決方法:**
トリガーが`status`を変更している場合、トリガーを削除または修正

### 3. Supabaseクライアントの問題

**確認方法:**
サーバーログで以下を確認：
- `[create_article] 送信するstatus値` と `[create_article] 生データのstatus` が一致しているか

**解決方法:**
コードで強制的に`status`を設定（既に実装済み）

### 4. タイミングの問題

**確認方法:**
`create_article`の後に即座に`get_article_by_id`で取得した値が異なるか

**解決方法:**
`create_article`関数内で、insert後に即座にselectして確認（既に実装済み）

## 実装済みの対策

1. **詳細なログ出力**
   - `create_article`関数で送信値と受信値を記録
   - データベースから直接再取得して確認

2. **強制的な更新**
   - `create_article`関数内で、statusが期待値と異なる場合に強制更新
   - `create_article_endpoint`で最終確認と強制更新

3. **複数回の確認**
   - 記事作成後
   - 進捗状況設定後
   - レスポンス返却前

## 次のステップ

1. **サーバーログを確認**
   - 上記のログが出力されているか確認
   - どの時点で`status`が`processing`になっているか特定

2. **データベースを確認**
   - `backend/check_articles_triggers.sql` を実行
   - トリガーや制約が`status`に影響していないか確認

3. **ログを共有**
   - サーバーログの該当部分を共有してください
   - 特に `[create_article]` で始まるログ

## 緊急時の対処

もし問題が続く場合、以下のSQLで強制的に修正できます：

```sql
-- 最近作成された記事でstatusがprocessingになっているものを修正
UPDATE articles
SET status = 'keyword_analysis'
WHERE status = 'processing'
AND created_at > NOW() - INTERVAL '1 hour'
AND keyword_analysis_progress IS NULL;
```

ただし、これは一時的な対処であり、根本原因を特定する必要があります。

