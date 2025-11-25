# ローカル動作確認用 .env ファイルの作成方法

## 手順

1. `backend`ディレクトリに移動
   ```bash
   cd backend
   ```

2. `.env`ファイルを作成
   ```bash
   touch .env
   # または
   # Windows: type nul > .env
   ```

3. 以下の内容をコピーして`.env`ファイルに貼り付け

```env
# Database (ローカルPostgreSQL)
# Docker Composeを使用する場合:
DATABASE_URL=postgresql://user:password@localhost:5432/article_generator

# Supabase (後で設定 - 今はコメントアウト)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your-anon-key

# JWT認証
SECRET_KEY=dev-secret-key-change-in-production-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API (記事生成に必要)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API (記事生成に必要)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google Gemini API (記事分析・変換に必要)
GEMINI_API_KEY=your-gemini-api-key-here

# Google Custom Search API (Google検索に必要)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CSE_ID=your-google-cse-id-here

# Shopify (後で設定 - 今はコメントアウト)
# SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
# SHOPIFY_ACCESS_TOKEN=your-shopify-access-token
# SHOPIFY_BLOG_ID=your-blog-id

# Environment
ENVIRONMENT=development

# CORS設定 (ローカル開発用)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
```

## 必須設定項目

ローカルで動作確認するために、**最低限以下を設定してください**：

### 1. DATABASE_URL
```env
DATABASE_URL=postgresql://user:password@localhost:5432/article_generator
```
- Docker Composeを使用する場合: 上記のままでOK
- ローカルPostgreSQLを使用する場合: `postgresql://postgres:your-password@localhost:5432/article_generator`

### 2. SECRET_KEY
```env
SECRET_KEY=dev-secret-key-change-in-production-minimum-32-characters-long
```
- 開発環境では上記のままでOK
- 本番環境では長いランダムな文字列を使用

### 3. APIキー（記事生成に必要）

以下のAPIキーを取得して設定してください：

#### OpenAI API
1. https://platform.openai.com/api-keys にアクセス
2. アカウントを作成/ログイン
3. "Create new secret key"をクリック
4. キーをコピーして設定
```env
OPENAI_API_KEY=sk-...
```

#### Anthropic API
1. https://console.anthropic.com/ にアクセス
2. アカウントを作成/ログイン
3. API Keysからキーを作成
4. キーをコピーして設定
```env
ANTHROPIC_API_KEY=sk-ant-...
```

#### Google Gemini API
1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. "Create API Key"をクリック
4. キーをコピーして設定
```env
GEMINI_API_KEY=...
```

#### Google Custom Search API
1. https://console.cloud.google.com/apis/credentials にアクセス
2. プロジェクトを作成
3. "Custom Search API"を有効化
4. 認証情報を作成（APIキー）
5. キーをコピーして設定
```env
GOOGLE_API_KEY=...
```

6. https://programmablesearchengine.google.com/ にアクセス
7. 検索エンジンを作成
8. 検索エンジンIDをコピーして設定
```env
GOOGLE_CSE_ID=...
```

## オプション設定（後で設定可能）

以下の設定は後で設定できます。今はコメントアウトしておいてOKです：

- `SUPABASE_URL` / `SUPABASE_ANON_KEY`: Supabaseセットアップ時に設定
- `SHOPIFY_*`: Shopify投稿機能を使用する場合に設定

## 動作確認

`.env`ファイルを作成したら：

```bash
# バックエンドを起動
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

エラーが発生しないことを確認してください。

