# DataForSEO認証情報の設定方法

## DataForSEOとは

DataForSEOは、SEO分析のためのAPIサービスです。キーワード分析、SERP分析、メタタグ生成などに使用されます。

## 認証情報の取得方法

### 1. DataForSEOアカウントの作成

1. **DataForSEOにアクセス**
   - https://dataforseo.com にアクセス

2. **アカウントを作成**
   - 「Sign Up」をクリック
   - アカウント情報を入力して登録

3. **ログイン**
   - 作成したアカウントでログイン

### 2. API認証情報の取得

1. **ダッシュボードにアクセス**
   - ログイン後、ダッシュボードに移動

2. **API認証情報を確認**
   - 「API」または「Settings」セクションを開く
   - 「API Credentials」または「Authentication」を確認
   - **Login** と **Password** をコピー

   **注意**: 
   - Loginは通常、メールアドレスまたはユーザー名
   - PasswordはAPI用のパスワード（アカウントのログインパスワードとは異なる場合があります）

### 3. Herokuに環境変数を設定

#### 方法1: Heroku CLIを使用（推奨）

```bash
# DataForSEO認証情報を設定
heroku config:set DATAFORSEO_LOGIN="your-dataforseo-login" --app blog-automation-api-prod
heroku config:set DATAFORSEO_PASSWORD="your-dataforseo-password" --app blog-automation-api-prod

# 設定を確認
heroku config:get DATAFORSEO_LOGIN --app blog-automation-api-prod
heroku config:get DATAFORSEO_PASSWORD --app blog-automation-api-prod

# アプリを再起動
heroku restart --app blog-automation-api-prod
```

#### 方法2: Herokuダッシュボードから設定

1. **Herokuダッシュボードにアクセス**
   - https://dashboard.heroku.com/apps/blog-automation-api-prod

2. **Settingsタブを開く**

3. **Config Varsセクションで「Reveal Config Vars」をクリック**

4. **以下の環境変数を追加**
   - **Key**: `DATAFORSEO_LOGIN`
     - **Value**: DataForSEOのログイン（メールアドレスまたはユーザー名）
   - **Key**: `DATAFORSEO_PASSWORD`
     - **Value**: DataForSEOのAPIパスワード

5. **「Add」をクリック**

6. **アプリを再起動**
   - 「More」メニューから「Restart all dynos」を選択

## 確認方法

### 1. 環境変数が正しく設定されているか確認

```bash
heroku config:get DATAFORSEO_LOGIN --app blog-automation-api-prod
heroku config:get DATAFORSEO_PASSWORD --app blog-automation-api-prod
```

### 2. アプリを再起動

```bash
heroku restart --app blog-automation-api-prod
```

### 3. ログを確認

```bash
heroku logs --tail --app blog-automation-api-prod
```

### 4. キーワード分析をテスト

- 「キーワード分析」タブで記事を選択
- 「キーワード分析を開始」ボタンをクリック
- エラーが発生しないか確認

## トラブルシューティング

### エラー: "DataForSEO設定が完了していません"

1. **環境変数が設定されているか確認**
   ```bash
   heroku config:get DATAFORSEO_LOGIN --app blog-automation-api-prod
   heroku config:get DATAFORSEO_PASSWORD --app blog-automation-api-prod
   ```

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

### エラー: "Payment Required"

DataForSEOアカウントに残高がない可能性があります。

1. **DataForSEOダッシュボードにアクセス**
2. **残高を確認**
3. **必要に応じてクレジットを追加**

### エラー: "Invalid credentials"

認証情報が間違っている可能性があります。

1. **DataForSEOダッシュボードで認証情報を再確認**
2. **環境変数を再設定**
3. **アプリを再起動**

## 参考

- DataForSEO公式サイト: https://dataforseo.com
- DataForSEO API ドキュメント: https://docs.dataforseo.com

## 注意事項

- **セキュリティ**: 認証情報は機密情報です。GitHubなどにコミットしないでください
- **環境変数**: Herokuの環境変数に設定することで、コードに直接書く必要がありません
- **残高**: DataForSEO APIを使用するには、アカウントに残高が必要です

