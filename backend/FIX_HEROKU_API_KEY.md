# Heroku APIキーの再生成と設定方法

## 問題

GitHub Actionsで以下のエラーが発生しています：
```
Error: The token provided to HEROKU_API_KEY is invalid.
```

## 原因

GitHub Actionsのシークレットに設定されている`HEROKU_API_KEY`が無効になっています。

## 解決方法

### 1. Heroku APIキーを再生成

#### 方法1: Heroku CLIを使用

```bash
# Herokuにログイン
heroku login

# APIキーを生成
heroku auth:token
```

このコマンドを実行すると、新しいAPIキーが表示されます。このキーをコピーしてください。

#### 方法2: Herokuダッシュボードから取得

1. **Herokuダッシュボードにアクセス**
   - https://dashboard.heroku.com/account

2. **「API Key」セクションを開く**

3. **「Reveal」または「Regenerate」をクリック**
   - 既存のキーを表示するか、新しいキーを生成

4. **APIキーをコピー**

### 2. GitHub Actionsのシークレットを更新

1. **GitHubリポジトリにアクセス**
   - https://github.com/NSDKIT/blog_automation

2. **Settingsタブを開く**

3. **「Secrets and variables」→「Actions」をクリック**

4. **`HEROKU_API_KEY`を更新**
   - `HEROKU_API_KEY`をクリック
   - 「Update」をクリック
   - 新しいAPIキーを貼り付け
   - 「Update secret」をクリック

### 3. デプロイを再実行

GitHub Actionsのシークレットを更新したら、デプロイを再実行してください：

1. **GitHub Actionsページにアクセス**
   - https://github.com/NSDKIT/blog_automation/actions

2. **最新のワークフロー実行を選択**

3. **「Re-run jobs」をクリック**

または、空のコミットをプッシュしてデプロイをトリガー：

```bash
git commit --allow-empty -m "trigger: GitHub Actionsデプロイを再実行"
git push origin main
```

## 確認方法

### 1. APIキーが正しいか確認

```bash
# Heroku CLIでログイン（APIキーを使用）
echo "your-api-key" | heroku login --interactive
```

### 2. GitHub Actionsのデプロイを確認

- https://github.com/NSDKIT/blog_automation/actions
- 最新のワークフロー実行が成功するか確認

## トラブルシューティング

### エラー: "The token provided to HEROKU_API_KEY is invalid"

1. **APIキーが正しくコピーされているか確認**
   - スペースや改行が含まれていないか確認
   - 完全にコピーされているか確認

2. **APIキーを再生成**
   - 新しいAPIキーを生成して、GitHub Actionsのシークレットを更新

3. **GitHub Actionsのシークレットを確認**
   - シークレットが正しく設定されているか確認
   - タイポがないか確認

### エラー: "Permission denied"

1. **Herokuアプリへのアクセス権限を確認**
   ```bash
   heroku apps:info --app blog-automation-api-prod
   ```

2. **Herokuアカウントが正しいか確認**
   - GitHub Actionsで使用しているメールアドレスとHerokuアカウントのメールアドレスが一致しているか確認

## 参考

- Heroku APIキー: https://devcenter.heroku.com/articles/authentication
- GitHub Actions シークレット: https://docs.github.com/en/actions/security-guides/encrypted-secrets

