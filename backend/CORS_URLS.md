# CORS設定に含めるべきURL

## 本番環境のフロントエンドURL

### 1. VercelのデプロイURL（本番環境）

**現在のURL**: `https://blog-automation-nu.vercel.app`

このURLは以下の方法で確認できます：

#### 方法1: ブラウザのエラーメッセージから確認
- CORSエラーメッセージに表示されている `origin` がフロントエンドのURLです
- 例: `from origin 'https://blog-automation-nu.vercel.app'`

#### 方法2: Vercelダッシュボードから確認
1. https://vercel.com にログイン
2. プロジェクト `blog-automation` を選択
3. 「Deployments」タブを開く
4. 最新のデプロイメントのURLを確認

#### 方法3: ブラウザのアドレスバーから確認
- 実際にアクセスしているURLがフロントエンドのURLです

### 2. ローカル開発用のURL

- `http://localhost:3000` - Viteのデフォルトポート（開発サーバー）
- `http://localhost:5173` - Viteの代替ポート
- `http://127.0.0.1:3000` - localhostの代替表記
- `http://127.0.0.1:5173` - localhostの代替表記

## 推奨されるCORS設定

### Herokuの環境変数

```bash
CORS_ORIGINS="https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
```

### コードのデフォルト値

現在のコード（`backend/app/config.py`）では、以下のデフォルト値が設定されています：

```python
cors_origins_str: str = "http://localhost:3000,http://localhost:5173,https://blog-automation-nu.vercel.app"
```

## 複数のVercel URLがある場合

Vercelでは、以下のようなURLが生成されることがあります：

- `https://blog-automation-nu.vercel.app` - プロダクションURL
- `https://blog-automation-nu-*.vercel.app` - プレビューURL（ブランチごと）

すべてのプレビューURLを許可する場合は、ワイルドカードを使用することもできますが、セキュリティ上の理由から推奨されません。

## 確認方法

### 1. 現在のCORS設定を確認

```bash
# Herokuの環境変数を確認
heroku config:get CORS_ORIGINS --app blog-automation-api-prod

# または、すべての環境変数を確認
heroku config --app blog-automation-api-prod
```

### 2. アプリのログで確認

```bash
heroku logs --tail --app blog-automation-api-prod
```

ログに `[CORS] Allowed origins: ...` が表示され、正しいURLが含まれているか確認してください。

### 3. ブラウザの開発者ツールで確認

1. ブラウザの開発者ツールを開く（F12）
2. 「Network」タブを開く
3. リクエストを送信
4. リクエストの「Headers」タブで `Origin` ヘッダーを確認
5. レスポンスの「Headers」タブで `Access-Control-Allow-Origin` ヘッダーを確認

## トラブルシューティング

### URLが正しく設定されているのにエラーが発生する場合

1. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

2. **環境変数の形式を確認**
   - カンマ区切りで、スペースなし
   - 例: `https://example.com,http://localhost:3000`

3. **ログを確認**
   ```bash
   heroku logs --tail --app blog-automation-api-prod | grep CORS
   ```

## 参考

- FastAPI CORS設定: https://fastapi.tiangolo.com/tutorial/cors/
- Vercel URL: https://vercel.com/docs/concepts/projects/domains

