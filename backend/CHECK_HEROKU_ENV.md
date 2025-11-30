# Heroku環境変数の確認と設定方法

## 問題

GitHub Actionsでデプロイ後、ログインできなくなった場合、環境変数が失われている可能性があります。

## 確認方法

### 1. Heroku CLIで環境変数を確認

```bash
# すべての環境変数を確認
heroku config --app blog-automation-api-prod

# 特定の環境変数を確認
heroku config:get CORS_ORIGINS --app blog-automation-api-prod
heroku config:get SECRET_KEY --app blog-automation-api-prod
heroku config:get SUPABASE_URL --app blog-automation-api-prod
```

### 2. Herokuダッシュボードで確認

1. https://dashboard.heroku.com/apps/blog-automation-api-prod にアクセス
2. 「Settings」タブを開く
3. 「Config Vars」セクションで「Reveal Config Vars」をクリック
4. 必要な環境変数が設定されているか確認

## 必要な環境変数

### 必須環境変数

```bash
# CORS設定
CORS_ORIGINS="https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173"

# JWT認証
SECRET_KEY="your-secret-key-here"

# Supabase
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-anon-key"

# OpenAI
OPENAI_API_KEY="your-openai-key"

# DataForSEO
DATAFORSEO_LOGIN="your-dataforseo-login"
DATAFORSEO_PASSWORD="your-dataforseo-password"
```

### オプション環境変数

```bash
# Anthropic
ANTHROPIC_API_KEY="your-anthropic-key"

# Google
GOOGLE_API_KEY="your-google-key"
GOOGLE_CSE_ID="your-google-cse-id"

# Gemini
GEMINI_API_KEY="your-gemini-key"

# Shopify
SHOPIFY_SHOP_DOMAIN="your-shop.myshopify.com"
SHOPIFY_ACCESS_TOKEN="your-shopify-token"
SHOPIFY_BLOG_ID="your-blog-id"

# Environment
ENVIRONMENT="production"
```

## 環境変数の設定方法

### 方法1: Heroku CLIを使用（推奨）

```bash
# 個別に設定
heroku config:set CORS_ORIGINS="https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173" --app blog-automation-api-prod
heroku config:set SECRET_KEY="your-secret-key" --app blog-automation-api-prod
heroku config:set SUPABASE_URL="https://your-project.supabase.co" --app blog-automation-api-prod
heroku config:set SUPABASE_ANON_KEY="your-anon-key" --app blog-automation-api-prod
heroku config:set OPENAI_API_KEY="your-openai-key" --app blog-automation-api-prod
heroku config:set DATAFORSEO_LOGIN="your-dataforseo-login" --app blog-automation-api-prod
heroku config:set DATAFORSEO_PASSWORD="your-dataforseo-password" --app blog-automation-api-prod

# アプリを再起動
heroku restart --app blog-automation-api-prod
```

### 方法2: Herokuダッシュボードから設定

1. https://dashboard.heroku.com/apps/blog-automation-api-prod にアクセス
2. 「Settings」タブを開く
3. 「Config Vars」セクションで「Reveal Config Vars」をクリック
4. 「Add」ボタンをクリック
5. KeyとValueを入力して「Add」をクリック
6. すべての環境変数を設定したら、アプリを再起動

## 環境変数が失われた場合の対処

### 1. バックアップから復元

以前の環境変数のバックアップがあれば、それを使用してください。

### 2. 新規に設定

上記の「環境変数の設定方法」を参照して、必要な環境変数を再設定してください。

## 確認手順

1. **環境変数を確認**
   ```bash
   heroku config --app blog-automation-api-prod
   ```

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

3. **ログを確認**
   ```bash
   heroku logs --tail --app blog-automation-api-prod
   ```

4. **再度ログインを試す**
   - ブラウザで https://blog-automation-nu.vercel.app にアクセス
   - ログインを試す

## トラブルシューティング

### CORSエラーが続く場合

1. **CORS_ORIGINSが正しく設定されているか確認**
   ```bash
   heroku config:get CORS_ORIGINS --app blog-automation-api-prod
   ```

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

3. **ログでCORS設定を確認**
   ```bash
   heroku logs --tail --app blog-automation-api-prod | grep CORS
   ```

### 認証エラーが発生する場合

1. **SECRET_KEYが設定されているか確認**
   ```bash
   heroku config:get SECRET_KEY --app blog-automation-api-prod
   ```

2. **Supabaseの設定が正しいか確認**
   ```bash
   heroku config:get SUPABASE_URL --app blog-automation-api-prod
   heroku config:get SUPABASE_ANON_KEY --app blog-automation-api-prod
   ```

## 参考

- Heroku環境変数の設定: https://devcenter.heroku.com/articles/config-vars
- Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

