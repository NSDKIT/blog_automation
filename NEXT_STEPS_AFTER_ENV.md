# 環境変数設定後の次のステップ

## ✅ 完了したこと
- [x] DATABASE_URL を設定
- [x] SUPABASE_URL を設定
- [x] SUPABASE_ANON_KEY を設定

## 📋 次にやること

### ステップ1: Supabaseでテーブルを作成

1. **Supabaseダッシュボードにアクセス**
   - https://supabase.com にログイン
   - プロジェクトを選択

2. **SQL Editorを開く**
   - 左メニューから「SQL Editor」をクリック
   - 「New query」をクリック

3. **SQLスクリプトを実行**
   - `backend/supabase_tables.sql` の内容をコピー
   - SQL Editorに貼り付け
   - 「Run」ボタンをクリック（または Cmd/Ctrl + Enter）

4. **テーブルの確認**
   - 左メニューから「Table Editor」をクリック
   - 以下のテーブルが作成されていることを確認：
     - ✅ `users`
     - ✅ `articles`
     - ✅ `article_histories`
     - ✅ `settings`
     - ✅ `knowledge_base`
     - ✅ `images`

### ステップ2: データベース接続の確認

```bash
cd backend

# 仮想環境を有効化（まだの場合）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール（まだの場合）
pip install -r requirements.txt

# データベース接続をテスト
python -c "from app.database import engine; print('接続成功!' if engine.connect() else '接続失敗')"
```

### ステップ3: データベースマイグレーション（必要に応じて）

Alembicを使用してテーブルを作成する場合：

```bash
cd backend

# マイグレーションファイルを作成（初回のみ）
alembic revision --autogenerate -m "Initial migration"

# マイグレーションを実行
alembic upgrade head
```

**注意**: SupabaseでSQLスクリプトを実行した場合は、このステップは不要です。

### ステップ4: バックエンドの起動と動作確認

```bash
cd backend

# バックエンドを起動
uvicorn app.main:app --reload
```

起動したら、以下にアクセスして確認：

- **API**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

### ステップ5: フロントエンドの起動（別ターミナル）

```bash
cd frontend

# 依存関係をインストール（まだの場合）
npm install

# フロントエンドを起動
npm run dev
```

起動したら、以下にアクセス：

- **アプリ**: http://localhost:3000

### ステップ6: 動作確認

1. **ユーザー登録**
   - http://localhost:3000 にアクセス
   - 「新規登録」でアカウントを作成

2. **ログイン**
   - 作成したアカウントでログイン

3. **記事生成のテスト**
   - ダッシュボードから「新規記事生成」をクリック
   - 必要な情報を入力
   - 記事を生成

## 🔍 トラブルシューティング

### エラー: "connection refused" または "could not connect"

**原因**: DATABASE_URLが正しくない、またはSupabaseの接続が許可されていない

**解決方法**:
1. `.env`ファイルの`DATABASE_URL`を確認
2. パスワードが正しいか確認
3. Supabaseダッシュボードで接続情報を再確認

### エラー: "relation does not exist"

**原因**: テーブルが作成されていない

**解決方法**:
1. SupabaseのSQL Editorで`supabase_tables.sql`を実行
2. Table Editorでテーブルが作成されているか確認

### エラー: "invalid API key"

**原因**: SUPABASE_ANON_KEYが正しくない

**解決方法**:
1. Supabaseダッシュボード → Settings → API
2. `anon public` キーを再確認
3. `.env`ファイルを更新

### エラー: "Module not found"

**原因**: 依存関係がインストールされていない

**解決方法**:
```bash
cd backend
pip install -r requirements.txt
```

## ✅ チェックリスト

- [ ] Supabaseでテーブルを作成した
- [ ] データベース接続が成功した
- [ ] バックエンドが起動した（http://localhost:8000/health が動作）
- [ ] フロントエンドが起動した（http://localhost:3000 が表示）
- [ ] ユーザー登録ができた
- [ ] ログインができた
- [ ] 記事生成が動作した（APIキーが設定されている場合）

## 📝 次のステップ

すべてのチェックが完了したら：

1. **APIキーの設定**
   - OpenAI, Anthropic, Gemini, Google APIキーを設定
   - 詳細は `API_KEYS_GUIDE.md` を参照

2. **GitHubにプッシュ**
   - `GITHUB_SETUP.md` を参照

3. **デプロイ**
   - `DEPLOY.md` を参照

