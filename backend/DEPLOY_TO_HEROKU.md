# Herokuへの手動デプロイ方法

## 問題

404エラーが発生している場合、Herokuに最新のコードがデプロイされていない可能性があります。

## 解決方法

### 方法1: GitHub Actionsのデプロイ状況を確認

1. **GitHubリポジトリにアクセス**
   - https://github.com/NSDKIT/blog_automation
   - 「Actions」タブをクリック

2. **最新のデプロイを確認**
   - 最新のワークフロー実行を確認
   - 成功（緑色のチェックマーク）か失敗（赤色のX）かを確認

3. **デプロイが失敗している場合**
   - エラーログを確認
   - 必要に応じて修正

### 方法2: Herokuに手動でデプロイ

GitHub Actionsが動作していない場合、手動でデプロイできます：

```bash
# 1. Heroku CLIにログイン
heroku login

# 2. Herokuアプリを確認
heroku apps

# 3. リモートリポジトリを確認
git remote -v

# 4. Herokuリモートが設定されていない場合、追加
heroku git:remote -a blog-automation-api-prod

# 5. バックエンドディレクトリに移動
cd backend

# 6. Herokuにデプロイ
git push heroku main

# または、現在のブランチから
git push heroku HEAD:main
```

### 方法3: Heroku CLIから直接デプロイ

```bash
# バックエンドディレクトリに移動
cd backend

# Herokuにデプロイ
heroku git:remote -a blog-automation-api-prod
git push heroku main
```

### デプロイ後の確認

```bash
# 1. ログを確認
heroku logs --tail --app blog-automation-api-prod

# 2. エンドポイントを確認
curl https://blog-automation-api-prod-1077654888a6.herokuapp.com/health

# 3. エンドポイントの存在を確認
curl -X POST https://blog-automation-api-prod-1077654888a6.herokuapp.com/api/articles/test-id/start-keyword-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## トラブルシューティング

### エラー: "remote heroku already exists"

```bash
# 既存のリモートを削除
git remote remove heroku

# 再度追加
heroku git:remote -a blog-automation-api-prod
```

### エラー: "Permission denied"

```bash
# Herokuにログイン
heroku login

# アプリへのアクセス権限を確認
heroku apps:info --app blog-automation-api-prod
```

### デプロイは成功したが、まだ404エラー

1. **Herokuのログを確認**
   ```bash
   heroku logs --tail --app blog-automation-api-prod
   ```

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

3. **エンドポイントのパスを確認**
   - 正しいパス: `/api/articles/{article_id}/start-keyword-analysis`
   - リクエストURLが正しいか確認

## 次のステップ

1. **GitHub Actionsのデプロイ状況を確認**
2. **必要に応じて手動でデプロイ**
3. **デプロイ後、再度「キーワード分析を開始」ボタンを押して確認**

