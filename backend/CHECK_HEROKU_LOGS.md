# Herokuログの確認方法

## バックエンドのログを確認

バックエンドはHerokuにデプロイされているため、Herokuのログを確認する必要があります。

## 方法1: Heroku CLIを使用（推奨）

### インストール

```bash
# macOS
brew tap heroku/brew && brew install heroku

# ログイン
heroku login
```

### ログの確認

```bash
# リアルタイムでログを確認
heroku logs --tail --app blog-automation-api-prod

# 最新の100行を表示
heroku logs --num 100 --app blog-automation-api-prod

# 特定のキーワードでフィルタ
heroku logs --tail --app blog-automation-api-prod | grep "analyze_keywords_task"
heroku logs --tail --app blog-automation-api-prod | grep "create_article"
```

## 方法2: Herokuダッシュボードから確認

1. **Herokuダッシュボードにアクセス**
   - https://dashboard.heroku.com/
   - ログイン

2. **アプリを選択**
   - `blog-automation-api-prod` をクリック

3. **「More」メニューから「View logs」を選択**
   - または、右上の「View logs」ボタンをクリック

4. **リアルタイムでログを確認**
   - ログストリームが表示されます

## 確認すべきログ

### 記事作成時のログ

```
[create_article_endpoint] 記事作成開始
[create_article] 記事作成
[create_article_endpoint] 別スレッドでキーワード分析タスクを開始しました
[create_article_endpoint] ✓ スレッドは正常に実行中です
```

### キーワード分析タスクのログ

```
[analyze_keywords_task] ========== 開始 ==========
[analyze_keywords_task] article_id=..., user_id=...
[analyze_keywords_task] ステータスチェック完了: keyword_analysis
[analyze_keywords_task] OpenAIで関連キーワード100個を生成中...
[analyze_keywords_task] 生成されたキーワード数: 100
[analyze_keywords_task] OpenAI生成完了 - 進捗状況更新結果: True
```

### エラーログ

```
[analyze_keywords_task] エラー発生: ...
[analyze_keywords_task] トレースバック: ...
ERROR
Exception
```

## トラブルシューティング

### ログが表示されない場合

1. **アプリ名を確認**
   ```bash
   heroku apps
   ```

2. **アプリが実行中か確認**
   ```bash
   heroku ps --app blog-automation-api-prod
   ```

3. **環境変数を確認**
   ```bash
   heroku config --app blog-automation-api-prod
   ```

### ログが多すぎる場合

```bash
# 特定の時間範囲でフィルタ
heroku logs --tail --app blog-automation-api-prod | grep "2025-11-29"

# 特定の記事IDでフィルタ
heroku logs --tail --app blog-automation-api-prod | grep "be747735-84e2-4311-8332-a817f78e7e8f"
```

## 次のステップ

1. **Herokuのログを確認**
   - `heroku logs --tail --app blog-automation-api-prod`

2. **「記事を生成」ボタンを押す**

3. **以下のログを探す**
   - `[create_article_endpoint]` で始まるログ
   - `[analyze_keywords_task]` で始まるログ
   - エラーログ

4. **ログを共有**
   - 特に `[analyze_keywords_task]` で始まるログを共有してください

