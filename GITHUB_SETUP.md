# GitHubリポジトリへのプッシュ手順

## 1. リポジトリの初期化（初回のみ）

```bash
# プロジェクトディレクトリに移動
cd /Users/nsdkit/Desktop/Tech.iro/アプリ開発/記事生成

# Gitリポジトリを初期化（既に初期化済みの場合はスキップ）
git init

# .gitignoreが正しく設定されているか確認
cat .gitignore
```

## 2. リモートリポジトリの追加

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/NSDKIT/blog_automation.git

# 既存のリモートがある場合は削除してから追加
# git remote remove origin
# git remote add origin https://github.com/NSDKIT/blog_automation.git
```

## 3. ファイルの追加とコミット

```bash
# すべてのファイルをステージング
git add .

# コミット
git commit -m "Initial commit: メガネ記事案ジェネレーター - Supabase対応版"

# コミットメッセージの例
# git commit -m "feat: Supabaseで知識ベースと画像管理を実装
# - 知識ベース検索をSupabaseに移行
# - Google Sheetsの代わりにSupabaseで画像管理
# - Vercel/Herokuデプロイ設定を追加"
```

## 4. ブランチの設定とプッシュ

```bash
# メインブランチに切り替え（既にmainブランチの場合はスキップ）
git branch -M main

# リモートにプッシュ
git push -u origin main
```

## 5. GitHub Actionsの設定（オプション）

GitHub Actionsで自動デプロイする場合、GitHubリポジトリのSettings > Secretsに以下を追加：

- `HEROKU_API_KEY`: Heroku APIキー
- `HEROKU_APP_NAME`: Herokuアプリ名
- `HEROKU_EMAIL`: Herokuアカウントのメールアドレス

## トラブルシューティング

### 既存のリポジトリと競合する場合

```bash
# リモートの変更を取得
git pull origin main --allow-unrelated-histories

# 競合を解決してから再度コミット
git add .
git commit -m "Merge remote changes"
git push origin main
```

### .envファイルがコミットされそうな場合

```bash
# .envファイルを削除（既にコミット済みの場合）
git rm --cached backend/.env
git rm --cached frontend/.env

# .gitignoreを確認
# .envが含まれていることを確認

# 再度コミット
git commit -m "Remove .env files from repository"
```

### 大きなファイルが含まれている場合

```bash
# .gitignoreを確認
# node_modules, __pycache__, .venvなどが除外されているか確認

# 特定のファイルを除外
git rm --cached -r node_modules/
git rm --cached -r backend/__pycache__/
```

