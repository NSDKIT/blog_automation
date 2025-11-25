# デプロイメントガイド

## 前提条件

- Docker と Docker Compose がインストールされていること
- 必要なAPIキーが取得済みであること

## セットアップ手順

### 1. 環境変数の設定

```bash
cd backend
cp .env.example .env
```

`.env`ファイルを編集して、以下のAPIキーを設定してください：

- `OPENAI_API_KEY`: OpenAI APIキー
- `ANTHROPIC_API_KEY`: Anthropic APIキー
- `GEMINI_API_KEY`: Google Gemini APIキー
- `GOOGLE_API_KEY`: Google Custom Search APIキー
- `GOOGLE_CSE_ID`: Google Custom Search Engine ID
- `SHOPIFY_SHOP_DOMAIN`: Shopifyストアドメイン
- `SHOPIFY_ACCESS_TOKEN`: Shopifyアクセストークン
- `SHOPIFY_BLOG_ID`: ShopifyブログID
- `SECRET_KEY`: JWT署名用の秘密鍵（ランダムな文字列）

### 2. データベースの初期化

```bash
docker-compose up -d db
docker-compose exec backend alembic upgrade head
```

### 3. アプリケーションの起動

```bash
docker-compose up -d
```

### 4. アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## 本番環境へのデプロイ

### 推奨構成

- **フロントエンド**: Vercel, Netlify, または静的ホスティング
- **バックエンド**: AWS ECS, Google Cloud Run, またはHeroku
- **データベース**: AWS RDS, Google Cloud SQL, またはManaged PostgreSQL
- **Redis**: AWS ElastiCache, Google Cloud Memorystore, またはManaged Redis

### 環境変数の管理

本番環境では、環境変数を安全に管理してください：

- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- 環境変数管理サービス

### セキュリティチェックリスト

- [ ] HTTPSを有効化
- [ ] CORS設定を本番環境に合わせて調整
- [ ] APIキーを環境変数で管理
- [ ] データベース接続をSSL/TLSで保護
- [ ] ログから機密情報を除外
- [ ] レート制限を実装
- [ ] エラーメッセージから詳細情報を除外

## トラブルシューティング

### データベース接続エラー

```bash
docker-compose logs db
```

### バックエンドエラー

```bash
docker-compose logs backend
```

### フロントエンドエラー

```bash
docker-compose logs frontend
```

