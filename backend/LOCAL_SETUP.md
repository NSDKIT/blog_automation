# ローカル開発環境のセットアップ

## 1. 必要な環境

- Python 3.11以上
- Node.js 18以上
- PostgreSQL (Docker Composeを使用する場合は不要)
- Docker & Docker Compose (オプション)

## 2. データベースのセットアップ

### オプションA: Docker Composeを使用（推奨）

```bash
# プロジェクトルートで実行
docker-compose up -d db

# データベースが起動するまで待つ（約10秒）
# 接続確認
docker-compose exec db psql -U user -d article_generator -c "SELECT 1;"
```

### オプションB: ローカルPostgreSQLを使用

```bash
# PostgreSQLをインストール（macOS）
brew install postgresql@15
brew services start postgresql@15

# データベースを作成
createdb article_generator

# ユーザーを作成（必要に応じて）
psql postgres
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE article_generator TO user;
\q
```

## 3. 環境変数の設定

### バックエンド

```bash
cd backend
cp .env.example .env
```

`.env`ファイルを編集して、以下を設定：

1. **DATABASE_URL**: データベース接続URL
   - Docker Compose使用: `postgresql://user:password@localhost:5432/article_generator`
   - ローカルPostgreSQL: `postgresql://postgres:your-password@localhost:5432/article_generator`

2. **SECRET_KEY**: JWT署名用の秘密鍵（32文字以上推奨）
   - 開発環境では `dev-secret-key-change-in-production-minimum-32-characters-long` でOK
   - 本番環境では長いランダムな文字列を使用

3. **APIキー**: 以下のAPIキーを取得して設定
   - `OPENAI_API_KEY`: https://platform.openai.com/api-keys
   - `ANTHROPIC_API_KEY`: https://console.anthropic.com/
   - `GEMINI_API_KEY`: https://makersuite.google.com/app/apikey
   - `GOOGLE_API_KEY`: https://console.cloud.google.com/apis/credentials
   - `GOOGLE_CSE_ID`: https://programmablesearchengine.google.com/

### フロントエンド

```bash
cd frontend
cp .env.example .env
```

`.env`ファイルを編集：

```env
# ローカル開発時は空欄でOK（Viteのプロキシが使用される）
# VITE_API_URL=
```

## 4. バックエンドのセットアップ

```bash
cd backend

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# サーバーを起動
uvicorn app.main:app --reload
```

バックエンドが起動したら、以下にアクセス：
- API: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

## 5. フロントエンドのセットアップ

```bash
# 新しいターミナルを開く
cd frontend

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

フロントエンドが起動したら、以下にアクセス：
- アプリ: http://localhost:3000

## 6. 動作確認

1. **バックエンドの確認**
   ```bash
   curl http://localhost:8000/health
   # 期待される結果: {"status":"healthy"}
   ```

2. **フロントエンドの確認**
   - ブラウザで http://localhost:3000 にアクセス
   - ログインページが表示されることを確認

3. **ユーザー登録・ログイン**
   - 新規登録でアカウントを作成
   - ログインしてダッシュボードにアクセス

4. **記事生成のテスト**
   - 新規記事生成ページに移動
   - 必要な情報を入力して記事を生成
   - **注意**: Supabaseが設定されていない場合、知識ベース検索と画像取得は空になります

## 7. トラブルシューティング

### データベース接続エラー

```bash
# データベースが起動しているか確認
docker-compose ps

# または
psql -U user -d article_generator -c "SELECT 1;"

# DATABASE_URLが正しいか確認
echo $DATABASE_URL
```

### ポートが既に使用されている

```bash
# ポート8000が使用されている場合
lsof -ti:8000 | xargs kill -9

# ポート3000が使用されている場合
lsof -ti:3000 | xargs kill -9
```

### マイグレーションエラー

```bash
# マイグレーションをリセット（開発環境のみ）
alembic downgrade base
alembic upgrade head
```

### APIキーエラー

- APIキーが正しく設定されているか確認
- `.env`ファイルが正しい場所にあるか確認（`backend/.env`）
- 環境変数が読み込まれているか確認

## 8. 開発時の注意事項

1. **Supabase未設定の場合**
   - 知識ベース検索は空文字列を返します
   - 画像取得は空配列を返します
   - 記事生成は動作しますが、知識ベースと画像なしで生成されます

2. **Shopify未設定の場合**
   - 記事生成は動作しますが、Shopifyへの投稿はエラーになります

3. **APIキーが設定されていない場合**
   - 該当する機能がエラーになります
   - エラーメッセージを確認して、必要なAPIキーを設定してください

