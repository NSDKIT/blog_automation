# メガネ記事案ジェネレーター

メガネ関連の記事を自動生成し、Shopifyに投稿するためのWebアプリケーション

**GitHub**: https://github.com/NSDKIT/blog_automation

## 機能

- キーワード、ターゲット層、記事の種類を入力して記事を自動生成
- Google検索結果を分析してSEO最適化された記事を作成
- 知識ベースから眼鏡生産者の想いを取得
- 画像を自動選定して記事に挿入
- Shopify形式に自動変換して投稿
- ユーザー認証・認可
- 記事履歴管理

## 技術スタック

- **フロントエンド**: React + TypeScript + Tailwind CSS
- **バックエンド**: Python + FastAPI
- **データベース**: PostgreSQL (Supabase / Heroku Postgres)
- **知識ベース・画像管理**: Supabase
- **認証**: JWT
- **デプロイ**: Vercel (フロントエンド) + Heroku (バックエンド)

## セットアップ

### 1. Supabaseのセットアップ

詳細は [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) を参照してください。

### 2. 環境変数の設定

```bash
cd backend
cp .env.example .env
# .envファイルを編集してAPIキーなどを設定
```

### 3. Docker Composeで起動

```bash
docker-compose up -d
```

### 4. データベースマイグレーション

```bash
docker-compose exec backend alembic upgrade head
```

## GitHubへのプッシュ

プロジェクトをGitHubにプッシュする手順は [GITHUB_PUSH.md](./GITHUB_PUSH.md) を参照してください。

## デプロイ

詳細は [DEPLOY.md](./DEPLOY.md) を参照してください。

- **フロントエンド**: Vercel（`frontend/vercel.json`で設定済み）
- **バックエンド**: Heroku（またはその他のホスティングサービス）

## API エンドポイント

### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - 現在のユーザー情報取得

### 記事
- `GET /api/articles` - 記事一覧取得
- `GET /api/articles/{id}` - 記事詳細取得
- `POST /api/articles` - 記事生成
- `PUT /api/articles/{id}` - 記事更新
- `DELETE /api/articles/{id}` - 記事削除
- `POST /api/articles/{id}/publish` - Shopifyに投稿

### 設定
- `GET /api/settings` - 設定取得
- `PUT /api/settings` - 設定更新

## 開発

### バックエンド開発

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

## デプロイ

本番環境へのデプロイは、各環境に応じて設定してください。

## ライセンス

MIT

