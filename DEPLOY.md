# デプロイガイド

## GitHubへのプッシュ

```bash
# リポジトリを初期化（既に初期化済みの場合はスキップ）
git init

# リモートリポジトリを追加
git remote add origin https://github.com/NSDKIT/blog_automation.git

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit: メガネ記事案ジェネレーター"

# プッシュ
git push -u origin main
```

## Vercelでのデプロイ（フロントエンド）

### 1. Vercelに接続

1. [Vercel](https://vercel.com)にログイン（GitHubアカウントでログイン推奨）
2. "New Project"をクリック
3. GitHubリポジトリ `NSDKIT/blog_automation` を選択
4. **Root Directory**: `frontend` に設定（重要！）

### 2. ビルド設定

Vercelは自動的にViteを検出しますが、以下の設定を確認：

- **Framework Preset**: Vite（自動検出）
- **Build Command**: `npm run build`（自動設定）
- **Output Directory**: `dist`（自動設定）
- **Install Command**: `npm install`（自動設定）

**注意**: `frontend/vercel.json`が存在するため、設定は自動的に読み込まれます。

### 3. 環境変数の設定

Vercelダッシュボードの「Environment Variables」で以下を設定：

```
VITE_API_URL=https://your-backend-url.herokuapp.com
```

**重要**: 
- `your-backend-url.herokuapp.com` を実際のバックエンドURLに置き換えてください
- バックエンドがHeroku以外の場合は、そのURLを設定してください

### 4. デプロイ

"Deploy"ボタンをクリック

デプロイが完了すると、VercelからURLが提供されます（例: `https://your-app.vercel.app`）

### 5. APIリクエストのプロキシ設定

`frontend/vercel.json`でAPIリクエストをバックエンドにプロキシする設定が含まれています。

デプロイ後、`frontend/vercel.json`の`rewrites`セクションでバックエンドURLを更新してください：

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-actual-backend-url.herokuapp.com/api/$1"
    }
  ]
}
```

または、環境変数`VITE_API_URL`を設定することで、フロントエンドコードから直接バックエンドにリクエストを送信できます（CORS設定が必要）。

## Herokuでのデプロイ（バックエンド）

### 1. Heroku CLIのインストール

```bash
# macOS
brew tap heroku/brew && brew install heroku

# ログイン
heroku login
```

### 2. Herokuアプリの作成

```bash
cd backend
heroku create your-app-name
```

### 3. PostgreSQLアドオンの追加

```bash
heroku addons:create heroku-postgresql:mini
```

### 4. 環境変数の設定

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SUPABASE_URL=https://your-project.supabase.co
heroku config:set SUPABASE_ANON_KEY=your-anon-key
heroku config:set OPENAI_API_KEY=your-openai-api-key
heroku config:set ANTHROPIC_API_KEY=your-anthropic-api-key
heroku config:set GEMINI_API_KEY=your-gemini-api-key
heroku config:set GOOGLE_API_KEY=your-google-api-key
heroku config:set GOOGLE_CSE_ID=your-google-cse-id
heroku config:set SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
heroku config:set SHOPIFY_ACCESS_TOKEN=your-shopify-access-token
heroku config:set SHOPIFY_BLOG_ID=your-blog-id
heroku config:set ENVIRONMENT=production
heroku config:set CORS_ORIGINS=https://your-frontend.vercel.app
```

### 5. データベースマイグレーション

```bash
heroku run alembic upgrade head
```

### 6. デプロイ

```bash
git push heroku main
```

### 7. ログの確認

```bash
heroku logs --tail
```

## Supabaseでのデータベース設定

### オプション1: Supabase Postgresを使用

Heroku Postgresの代わりにSupabase Postgresを使用する場合：

1. Supabaseダッシュボードでプロジェクト設定を開く
2. Database > Connection string をコピー
3. Herokuの環境変数に設定：

```bash
heroku config:set DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
```

### オプション2: Supabaseのみを使用

PostgreSQLをSupabaseのみで管理する場合、`backend/app/database.py`を修正してSupabaseの接続を使用。

## デプロイ後の確認

### フロントエンド

- https://your-app.vercel.app にアクセス
- ログインページが表示されることを確認

### バックエンド

- https://your-app.herokuapp.com/health にアクセス
- `{"status": "healthy"}` が返ることを確認
- https://your-app.herokuapp.com/docs でAPIドキュメントを確認

## トラブルシューティング

### Herokuデプロイエラー

```bash
# ログを確認
heroku logs --tail

# アプリを再起動
heroku restart
```

### Vercelビルドエラー

- VercelダッシュボードのBuild Logsを確認
- 環境変数が正しく設定されているか確認

### データベース接続エラー

```bash
# Heroku Postgresの接続情報を確認
heroku config:get DATABASE_URL

# 接続テスト
heroku run python -c "from app.database import engine; print(engine.connect())"
```

