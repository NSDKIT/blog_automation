# セットアップガイド - 今すぐやること

## 🎯 優先順位順の手順

### ステップ1: Supabaseプロジェクトの作成（最優先）

1. **Supabaseアカウントを作成**
   - https://supabase.com にアクセス
   - GitHubアカウントでログイン（推奨）

2. **新しいプロジェクトを作成**
   - "New Project"をクリック
   - プロジェクト名を入力（例: `blog-automation`）
   - データベースパスワードを設定（必ずメモしてください！）
   - リージョンを選択（東京: `ap-northeast-1`推奨）
   - "Create new project"をクリック
   - プロジェクトの作成完了まで待つ（2-3分）

3. **APIキーを取得**
   - プロジェクトダッシュボードの「Settings」→「API」を開く
   - `Project URL` をコピー → これが `SUPABASE_URL`
   - `anon public` キーをコピー → これが `SUPABASE_ANON_KEY`

4. **テーブルを作成**
   - プロジェクトダッシュボードの「SQL Editor」を開く
   - 「New query」をクリック
   - `backend/supabase_tables_fixed.sql` の内容をすべてコピーして貼り付け
   - 「Run」ボタンをクリック
   - エラーがなければ成功です！

---

### ステップ2: 環境変数ファイルの作成

1. **`.env`ファイルを作成**
   ```bash
   cd backend
   touch .env
   ```

2. **以下の内容を`.env`ファイルに貼り付け**
   ```env
   # ============================================
   # Supabase設定（必須）
   # ============================================
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here

   # ============================================
   # JWT認証設定（必須）
   # ============================================
   SECRET_KEY=dev-secret-key-change-in-production-minimum-32-characters-long
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # ============================================
   # AI API設定（記事生成に必要）
   # ============================================
   OPENAI_API_KEY=your-openai-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   GOOGLE_API_KEY=your-google-api-key-here
   GOOGLE_CSE_ID=your-google-cse-id-here

   # ============================================
   # その他の設定
   # ============================================
   ENVIRONMENT=development
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
   ```

3. **Supabaseの値を設定**
   - ステップ1で取得した `SUPABASE_URL` と `SUPABASE_ANON_KEY` を貼り付け

---

### ステップ3: APIキーの取得（記事生成機能を使う場合）

記事生成機能を使うには、以下のAPIキーが必要です：

#### OpenAI API
1. https://platform.openai.com/api-keys にアクセス
2. アカウントを作成/ログイン
3. "Create new secret key"をクリック
4. キーをコピーして`.env`の`OPENAI_API_KEY`に設定

#### Anthropic API
1. https://console.anthropic.com/ にアクセス
2. アカウントを作成/ログイン
3. API Keysからキーを作成
4. キーをコピーして`.env`の`ANTHROPIC_API_KEY`に設定

#### Google Gemini API
1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. "Create API Key"をクリック
4. キーをコピーして`.env`の`GEMINI_API_KEY`に設定

#### Google Custom Search API
1. https://console.cloud.google.com/apis/credentials にアクセス
2. プロジェクトを作成
3. "Custom Search API"を有効化
4. 認証情報を作成（APIキー）
5. キーをコピーして`.env`の`GOOGLE_API_KEY`に設定
6. https://programmablesearchengine.google.com/ にアクセス
7. 検索エンジンを作成
8. 検索エンジンIDをコピーして`.env`の`GOOGLE_CSE_ID`に設定

**注意**: まずはSupabaseの設定だけで動作確認できます。APIキーは後で設定してもOKです。

---

### ステップ4: バックエンドの起動確認

1. **仮想環境の作成と依存関係のインストール**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **バックエンドを起動**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **動作確認**
   - ブラウザで http://localhost:8000/health にアクセス
   - `{"status":"healthy"}` が表示されればOK
   - http://localhost:8000/docs でAPIドキュメントも確認できます

---

### ステップ5: フロントエンドの起動確認

1. **依存関係のインストール**
   ```bash
   cd frontend
   npm install
   ```

2. **フロントエンドを起動**
   ```bash
   npm run dev
   ```

3. **動作確認**
   - ブラウザで http://localhost:5173 にアクセス
   - ログインページが表示されればOK

---

## ✅ チェックリスト

- [ ] Supabaseプロジェクトを作成
- [ ] SupabaseのAPIキーを取得
- [ ] Supabaseでテーブルを作成（`supabase_tables_fixed.sql`を実行）
- [ ] `backend/.env`ファイルを作成
- [ ] Supabaseの環境変数を設定
- [ ] バックエンドを起動して動作確認
- [ ] フロントエンドを起動して動作確認
- [ ] （オプション）APIキーを取得して設定

---

## 🆘 トラブルシューティング

### Supabase接続エラー
- `SUPABASE_URL` と `SUPABASE_ANON_KEY` が正しいか確認
- Supabaseダッシュボードでテーブルが作成されているか確認

### バックエンド起動エラー
- 仮想環境が有効になっているか確認: `which python` で `venv/bin/python` が表示されるはず
- 依存関係がインストールされているか確認: `pip list | grep fastapi`

### フロントエンド起動エラー
- Node.jsのバージョンを確認: `node --version` （18以上推奨）
- `node_modules`を削除して再インストール: `rm -rf node_modules && npm install`

---

## 📚 参考ドキュメント

- `SUPABASE_SETUP.md` - Supabaseセットアップの詳細
- `CURRENT_STATUS.md` - 現在のプロジェクト状態
- `NEXT_STEPS.md` - 次のステップ（デプロイなど）

