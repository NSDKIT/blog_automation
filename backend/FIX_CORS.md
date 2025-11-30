# CORSエラーの修正方法

## 問題

ログイン時にCORSエラーが発生しています：
```
Access to XMLHttpRequest at 'https://blog-automation-api-prod-1077654888a6.herokuapp.com/api/auth/login' 
from origin 'https://blog-automation-nu.vercel.app' has been blocked by CORS policy
```

## 原因

Herokuの環境変数に`CORS_ORIGINS`が設定されていないか、VercelのURLが含まれていません。

## 解決方法

Herokuの環境変数に`CORS_ORIGINS`を設定してください。

### 方法1: Heroku CLIを使用

```bash
# Herokuにログイン
heroku login

# CORS_ORIGINSを設定
heroku config:set CORS_ORIGINS="https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173" --app blog-automation-api-prod

# 設定を確認
heroku config --app blog-automation-api-prod
```

### 方法2: Herokuダッシュボードから設定

1. **Herokuダッシュボードにアクセス**
   - https://dashboard.heroku.com/apps/blog-automation-api-prod

2. **Settingsタブを開く**

3. **Config Varsセクションで「Reveal Config Vars」をクリック**

4. **以下の環境変数を追加/更新**
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173`

5. **「Add」または「Save」をクリック**

### 方法3: 複数のオリジンを設定する場合

複数のフロントエンドURLを許可する場合：

```bash
heroku config:set CORS_ORIGINS="https://blog-automation-nu.vercel.app,https://your-other-domain.com,http://localhost:3000,http://localhost:5173" --app blog-automation-api-prod
```

## 設定後の確認

1. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

2. **ログを確認**
   ```bash
   heroku logs --tail --app blog-automation-api-prod
   ```

3. **再度ログインを試す**
   - ブラウザで https://blog-automation-nu.vercel.app にアクセス
   - ログインを試す

## トラブルシューティング

### まだCORSエラーが発生する場合

1. **環境変数が正しく設定されているか確認**
   ```bash
   heroku config:get CORS_ORIGINS --app blog-automation-api-prod
   ```

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

3. **ブラウザのキャッシュをクリア**
   - ブラウザの開発者ツールを開く
   - 「Network」タブで「Disable cache」をチェック
   - ページをリロード

### 環境変数の形式

- **正しい形式**: `https://blog-automation-nu.vercel.app,http://localhost:3000`
- **間違った形式**: `["https://blog-automation-nu.vercel.app"]` (JSON配列は使用しない)

## 参考

- CORS設定は`backend/app/config.py`で定義されています
- `CORS_ORIGINS`環境変数はカンマ区切りの文字列として設定します

