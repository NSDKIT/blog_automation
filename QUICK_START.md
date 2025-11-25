# クイックスタートガイド

## ✅ 完了したこと
- [x] Supabaseでテーブルを作成

## 🚀 次のステップ

### 1. データベース接続の確認

```bash
cd backend

# 仮想環境を作成・有効化（初回のみ）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール（初回のみ）
pip install -r requirements.txt

# データベース接続をテスト
python -c "from app.database import engine; conn = engine.connect(); print('✅ データベース接続成功!'); conn.close()"
```

### 2. バックエンドの起動

```bash
cd backend
source venv/bin/activate  # 仮想環境が有効化されていることを確認

# バックエンドを起動
uvicorn app.main:app --reload
```

**起動確認**:
- ブラウザで http://localhost:8000/health にアクセス
- `{"status":"healthy"}` が表示されれば成功
- APIドキュメント: http://localhost:8000/docs

### 3. フロントエンドの起動（別ターミナル）

```bash
cd frontend

# 依存関係をインストール（初回のみ）
npm install

# フロントエンドを起動
npm run dev
```

**起動確認**:
- ブラウザで http://localhost:3000 にアクセス
- ログインページが表示されれば成功

### 4. 動作確認

1. **ユーザー登録**
   - http://localhost:3000 にアクセス
   - 「新規登録はこちら」をクリック
   - メールアドレス、パスワード、名前を入力して登録

2. **ログイン**
   - 登録したアカウントでログイン

3. **ダッシュボード確認**
   - ログイン後、ダッシュボードが表示されることを確認

4. **記事生成のテスト**（APIキーが設定されている場合）
   - 「新規記事生成」をクリック
   - 必要な情報を入力
   - 「記事を生成」をクリック

## ⚠️ 注意事項

### APIキーが未設定の場合

記事生成機能を使用するには、以下のAPIキーが必要です：
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

`.env`ファイルに設定してください。詳細は `API_KEYS_GUIDE.md` を参照。

### エラーが発生した場合

- **データベース接続エラー**: `.env`ファイルの`DATABASE_URL`を確認
- **モジュールが見つからない**: `pip install -r requirements.txt`を実行
- **ポートが使用中**: 別のアプリがポート8000や3000を使用していないか確認

## 📝 次のステップ

動作確認が完了したら：

1. **APIキーの設定** - `API_KEYS_GUIDE.md` を参照
2. **GitHubにプッシュ** - `GITHUB_SETUP.md` を参照
3. **デプロイ** - `DEPLOY.md` を参照

