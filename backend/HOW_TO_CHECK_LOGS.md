# サーバーログの確認方法

このドキュメントでは、バックエンドサーバーのログを確認する方法を説明します。

## ローカル開発環境の場合

### 方法1: ターミナルで直接確認（推奨）

バックエンドサーバーを起動しているターミナルウィンドウで、ログがリアルタイムで表示されます。

```bash
# バックエンドディレクトリに移動
cd backend

# サーバーを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

このターミナルに、以下のようなログが表示されます：

```
[create_article_endpoint] 記事作成開始: keyword=..., status=keyword_analysis
[create_article] 記事作成: status=keyword_analysis, article_data=...
[analyze_keywords_task] ========== 開始 ==========
```

### 方法2: Docker Composeを使用している場合

```bash
# プロジェクトルートで実行
docker-compose logs -f backend
```

または、特定のコンテナのログを確認：

```bash
docker-compose logs -f backend | grep "analyze_keywords_task"
```

### 方法3: ログをファイルに保存

```bash
# ログをファイルに保存しながら実行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee server.log
```

その後、`server.log`ファイルを確認：

```bash
# リアルタイムで確認
tail -f server.log

# 特定のキーワードで検索
grep "analyze_keywords_task" server.log
grep "create_article" server.log
```

## 本番環境（Heroku）の場合

### Heroku CLIを使用

```bash
# Heroku CLIをインストール（まだの場合）
# macOS
brew tap heroku/brew && brew install heroku

# ログイン
heroku login

# リアルタイムでログを確認（推奨）
heroku logs --tail --app your-app-name

# 最新の100行を表示
heroku logs --num 100 --app your-app-name

# 特定のキーワードでフィルタ
heroku logs --tail --app your-app-name | grep "analyze_keywords_task"
```

### Herokuダッシュボードから確認

1. [Heroku Dashboard](https://dashboard.heroku.com/) にアクセス
2. アプリを選択
3. 上部の「More」メニューから「View logs」を選択
4. または、右上の「View logs」ボタンをクリック

## 本番環境（その他のプラットフォーム）の場合

### Railway

```bash
# Railway CLIを使用
railway logs

# または、Railwayダッシュボードから
# https://railway.app/dashboard にアクセス
# プロジェクト > サービス > Logs タブ
```

### Render

```bash
# Renderダッシュボードから
# https://dashboard.render.com/ にアクセス
# サービス > Logs タブ
```

### AWS / Google Cloud / Azure

各プラットフォームのログサービスを使用：

- **AWS**: CloudWatch Logs
- **Google Cloud**: Cloud Logging
- **Azure**: Application Insights

## 確認すべきログのキーワード

問題を診断するために、以下のキーワードでログを検索してください：

### 記事作成関連

```bash
# 記事作成の流れ
grep "create_article_endpoint" server.log
grep "create_article" server.log
grep "記事作成" server.log
```

### キーワード分析関連

```bash
# キーワード分析タスク
grep "analyze_keywords_task" server.log
grep "キーワード分析" server.log
grep "OpenAIで" server.log
grep "DataForSEO" server.log
```

### エラー関連

```bash
# エラーを確認
grep "エラー" server.log
grep "ERROR" server.log
grep "Exception" server.log
grep "Traceback" server.log
```

### ステータス関連

```bash
# statusの変更を確認
grep "status=" server.log
grep "ステータス" server.log
```

## ログの例

正常な場合のログ例：

```
[create_article_endpoint] 記事作成開始: keyword=Python入門, status=keyword_analysis
[create_article] 記事作成: status=keyword_analysis, article_data={...}
[create_article] 記事作成完了: id=..., status=keyword_analysis
[create_article_endpoint] 別スレッドでキーワード分析タスクを開始しました
[create_article_endpoint] ✓ スレッドは正常に実行中です
[analyze_keywords_task] ========== 開始 ==========
[analyze_keywords_task] article_id=..., user_id=...
[analyze_keywords_task] ステータスチェック完了: keyword_analysis
[analyze_keywords_task] OpenAIで関連キーワード100個を生成中...
[analyze_keywords_task] 生成されたキーワード数: 100
[analyze_keywords_task] OpenAI生成完了 - 進捗状況更新結果: True
```

エラーが発生している場合のログ例：

```
[analyze_keywords_task] エラー発生: ...
[analyze_keywords_task] トレースバック:
Traceback (most recent call last):
  ...
```

## トラブルシューティング

### ログが表示されない場合

1. **サーバーが起動しているか確認**
   ```bash
   # ローカル
   curl http://localhost:8000/health
   
   # Heroku
   curl https://your-app-name.herokuapp.com/health
   ```

2. **環境変数を確認**
   ```bash
   # ローカル
   cat backend/.env
   
   # Heroku
   heroku config --app your-app-name
   ```

3. **ログレベルを確認**
   - Pythonの`print()`文は標準出力に出力されます
   - 本番環境では、ログサービス（CloudWatch、Stackdriverなど）を使用することを推奨

### ログが多すぎる場合

```bash
# 特定の時間範囲でフィルタ
heroku logs --tail --app your-app-name | grep "2025-01-28"

# 特定のユーザーIDでフィルタ
heroku logs --tail --app your-app-name | grep "user_id=xxx"
```

## 次のステップ

ログを確認したら、以下を共有してください：

1. **記事作成時のログ**（`create_article_endpoint`で始まるログ）
2. **キーワード分析タスクのログ**（`analyze_keywords_task`で始まるログ）
3. **エラーログ**（`エラー`、`ERROR`、`Exception`を含むログ）

これにより、問題の原因を特定できます。

