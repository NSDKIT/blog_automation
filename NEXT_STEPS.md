# 次のステップ - 実装チェックリスト

## ✅ 完了したこと
- [x] Supabase対応の実装
- [x] デプロイ設定ファイルの作成
- [x] ドキュメントの作成

## 📋 あなたが行うべき作業

### ステップ1: Supabaseプロジェクトの作成とセットアップ

1. **Supabaseアカウントの作成**
   - https://supabase.com にアクセス
   - アカウントを作成（GitHubアカウントでログイン可能）

2. **新しいプロジェクトを作成**
   - "New Project"をクリック
   - プロジェクト名を入力（例: `blog-automation`）
   - データベースパスワードを設定
   - リージョンを選択（東京: `ap-northeast-1`推奨）

3. **APIキーを取得**
   - プロジェクトダッシュボードの「Settings」→「API」
   - `Project URL` をコピー → これが `SUPABASE_URL`
   - `anon public` キーをコピー → これが `SUPABASE_ANON_KEY`

4. **テーブルの作成**
   - プロジェクトダッシュボードの「SQL Editor」を開く
   - `SUPABASE_SETUP.md` のSQLを実行
   - `knowledge_base` テーブルと `images` テーブルを作成

5. **サンプルデータの投入**
   - `SUPABASE_SETUP.md` のサンプルデータSQLを実行
   - または、手動でデータを追加

### ステップ2: ローカル環境の設定

1. **環境変数ファイルの作成**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **`.env`ファイルを編集**
   ```env
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   
   # その他のAPIキー
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GEMINI_API_KEY=your-gemini-key
   GOOGLE_API_KEY=your-google-key
   GOOGLE_CSE_ID=your-cse-id
   SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
   SHOPIFY_ACCESS_TOKEN=your-shopify-token
   SHOPIFY_BLOG_ID=your-blog-id
   
   # JWT
   SECRET_KEY=ランダムな文字列（本番環境では長い文字列を推奨）
   ```

3. **ローカルで動作確認**
   ```bash
   # バックエンドを起動
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   
   # 別ターミナルでフロントエンドを起動
   cd frontend
   npm install
   npm run dev
   ```

### ステップ3: GitHubリポジトリへのプッシュ

1. **Gitリポジトリの初期化（初回のみ）**
   ```bash
   cd /Users/nsdkit/Desktop/Tech.iro/アプリ開発/記事生成
   git init
   git remote add origin https://github.com/NSDKIT/blog_automation.git
   ```

2. **ファイルをコミット**
   ```bash
   git add .
   git commit -m "Initial commit: メガネ記事案ジェネレーター - Supabase対応版"
   ```

3. **GitHubにプッシュ**
   ```bash
   git branch -M main
   git push -u origin main
   ```

   **注意**: `.env`ファイルはコミットしないでください（`.gitignore`に含まれています）

### ステップ4: Herokuでバックエンドをデプロイ

1. **Heroku CLIのインストール**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # ログイン
   heroku login
   ```

2. **Herokuアプリの作成**
   ```bash
   cd backend
   heroku create your-app-name
   # 例: heroku create blog-automation-api
   ```

3. **PostgreSQLアドオンの追加**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **環境変数の設定**
   ```bash
   heroku config:set SUPABASE_URL=https://your-project.supabase.co
   heroku config:set SUPABASE_ANON_KEY=your-anon-key
   heroku config:set OPENAI_API_KEY=your-openai-key
   heroku config:set ANTHROPIC_API_KEY=your-anthropic-key
   heroku config:set GEMINI_API_KEY=your-gemini-key
   heroku config:set GOOGLE_API_KEY=your-google-key
   heroku config:set GOOGLE_CSE_ID=your-cse-id
   heroku config:set SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
   heroku config:set SHOPIFY_ACCESS_TOKEN=your-shopify-token
   heroku config:set SHOPIFY_BLOG_ID=your-blog-id
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set ENVIRONMENT=production
   ```

5. **データベースマイグレーション**
   ```bash
   heroku run alembic upgrade head
   ```

6. **デプロイ**
   ```bash
   git push heroku main
   ```

7. **動作確認**
   ```bash
   # ヘルスチェック
   curl https://your-app-name.herokuapp.com/health
   
   # ログ確認
   heroku logs --tail
   ```

### ステップ5: Vercelでフロントエンドをデプロイ

1. **Vercelにログイン**
   - https://vercel.com にアクセス
   - GitHubアカウントでログイン

2. **プロジェクトのインポート**
   - "New Project"をクリック
   - GitHubリポジトリ `NSDKIT/blog_automation` を選択
   - **Root Directory**: `frontend` に設定

3. **環境変数の設定**
   - Environment Variables に以下を追加：
     ```
     VITE_API_URL=https://your-app-name.herokuapp.com/api
     ```
   - `your-app-name` はHerokuアプリ名に置き換え

4. **ビルド設定の確認**
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

5. **デプロイ**
   - "Deploy"ボタンをクリック
   - デプロイが完了するまで待つ

6. **動作確認**
   - デプロイされたURLにアクセス
   - ログインページが表示されることを確認

### ステップ6: 動作テスト

1. **フロントエンドからバックエンドへの接続確認**
   - VercelのURLにアクセス
   - ユーザー登録・ログインができるか確認

2. **記事生成のテスト**
   - ログイン後、新規記事生成ページに移動
   - 必要な情報を入力して記事を生成
   - 生成が完了するまで待つ

3. **Supabase連携の確認**
   - Supabaseダッシュボードでデータが正しく取得されているか確認

## 🔧 トラブルシューティング

### エラーが発生した場合

1. **Herokuデプロイエラー**
   ```bash
   heroku logs --tail
   ```
   ログを確認してエラー内容を特定

2. **Vercelビルドエラー**
   - Vercelダッシュボードの「Deployments」→「Build Logs」を確認

3. **Supabase接続エラー**
   - `SUPABASE_URL` と `SUPABASE_ANON_KEY` が正しいか確認
   - Supabaseダッシュボードでテーブルが作成されているか確認

## 📚 参考ドキュメント

- `SUPABASE_SETUP.md` - Supabaseセットアップの詳細
- `DEPLOY.md` - デプロイ手順の詳細
- `GITHUB_SETUP.md` - GitHubリポジトリ設定の詳細

## ⚠️ 重要な注意事項

1. **APIキーの管理**
   - `.env`ファイルは絶対にGitHubにコミットしない
   - 本番環境では環境変数で管理

2. **セキュリティ**
   - `SECRET_KEY`は長いランダムな文字列を使用
   - SupabaseのRLS（Row Level Security）を適切に設定

3. **コスト管理**
   - Herokuの無料プランには制限がある
   - Supabaseの無料プランにも制限がある
   - 使用量を定期的に確認

