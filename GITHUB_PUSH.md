# GitHubへのプッシュ手順

このドキュメントでは、プロジェクトをGitHubにプッシュする手順を説明します。

## 前提条件

- Gitがインストールされていること
- GitHubアカウントを持っていること
- GitHubリポジトリ `NSDKIT/blog_automation` が作成済みであること

## 手順

### 1. Gitリポジトリの初期化（初回のみ）

```bash
cd /Users/nsdkit/Desktop/Tech.iro/アプリ開発/記事生成

# Gitリポジトリを初期化（既に初期化済みの場合はスキップ）
git init

# リモートリポジトリを追加
git remote add origin https://github.com/NSDKIT/blog_automation.git

# 既にリモートが設定されている場合は、以下で確認
git remote -v
```

### 2. 現在のブランチを確認

```bash
# 現在のブランチを確認
git branch

# mainブランチに切り替え（必要に応じて）
git checkout -b main
```

### 3. ファイルをステージング

```bash
# すべてのファイルを追加
git add .

# ステージングされたファイルを確認
git status
```

**注意**: `.env`ファイルは`.gitignore`に含まれているため、コミットされません。

### 4. コミット

```bash
git commit -m "Initial commit: メガネ記事案ジェネレーター - Vercelデプロイ対応"
```

### 5. GitHubにプッシュ

```bash
# mainブランチにプッシュ
git push -u origin main
```

初回プッシュ時は、GitHubの認証情報を求められる場合があります。

## 確認

プッシュが成功したら、以下を確認してください：

1. https://github.com/NSDKIT/blog_automation にアクセス
2. ファイルが正しくアップロードされているか確認
3. `.env`ファイルが含まれていないことを確認（セキュリティ上重要）

## 次のステップ

GitHubへのプッシュが完了したら、Vercelでデプロイできます：

1. [Vercel](https://vercel.com)にログイン
2. "New Project"をクリック
3. GitHubリポジトリ `NSDKIT/blog_automation` を選択
4. **Root Directory**: `frontend` に設定
5. 環境変数 `VITE_API_URL` を設定（バックエンドのURL）
6. "Deploy"をクリック

詳細は [DEPLOY.md](./DEPLOY.md) を参照してください。

## トラブルシューティング

### リモートリポジトリが既に存在する場合

```bash
# リモートを削除して再追加
git remote remove origin
git remote add origin https://github.com/NSDKIT/blog_automation.git
```

### プッシュが拒否される場合

```bash
# リモートの最新を取得
git pull origin main --allow-unrelated-histories

# 再度プッシュ
git push -u origin main
```

### .envファイルが誤ってコミットされた場合

```bash
# .envファイルをGitの追跡から削除（ファイル自体は残る）
git rm --cached backend/.env
git commit -m "Remove .env from git tracking"
git push
```

