# Herokuアプリのステータス確認方法

## 問題

503 Service Unavailableエラーが発生している場合、Herokuアプリがダウンしているか、起動に失敗している可能性があります。

## 確認手順

### 1. Herokuアプリのステータスを確認

```bash
# アプリのステータスを確認
heroku ps --app blog-automation-api-prod

# 詳細な情報を確認
heroku ps:scale --app blog-automation-api-prod
```

### 2. ログを確認

```bash
# 最新のログを確認
heroku logs --tail --app blog-automation-api-prod

# エラーログのみを確認
heroku logs --tail --app blog-automation-api-prod | grep -i error

# 起動時のログを確認
heroku logs --tail --app blog-automation-api-prod | grep -i "starting\|listening\|uvicorn"
```

### 3. アプリを再起動

```bash
# アプリを再起動
heroku restart --app blog-automation-api-prod

# すべてのdynoを再起動
heroku restart --app blog-automation-api-prod --dyno all
```

### 4. 必須環境変数が設定されているか確認

```bash
# すべての環境変数を確認
heroku config --app blog-automation-api-prod

# 必須環境変数を確認
heroku config:get SECRET_KEY --app blog-automation-api-prod
heroku config:get SUPABASE_URL --app blog-automation-api-prod
heroku config:get SUPABASE_ANON_KEY --app blog-automation-api-prod
```

## よくある原因と解決方法

### 1. アプリがクラッシュしている

**症状**: ログにエラーが表示される

**解決方法**:
1. ログを確認してエラーを特定
2. エラーを修正
3. アプリを再起動

### 2. 必須環境変数が設定されていない

**症状**: アプリが起動時にエラーで終了

**解決方法**:
1. 必須環境変数を設定
2. アプリを再起動

### 3. メモリ不足

**症状**: アプリが頻繁にクラッシュする

**解決方法**:
1. Herokuプランをアップグレード
2. または、アプリのメモリ使用量を最適化

### 4. データベース接続エラー

**症状**: Supabaseへの接続に失敗

**解決方法**:
1. SUPABASE_URLとSUPABASE_ANON_KEYが正しく設定されているか確認
2. Supabaseのダッシュボードで接続を確認

## トラブルシューティング手順

### ステップ1: アプリのステータスを確認

```bash
heroku ps --app blog-automation-api-prod
```

期待される出力:
```
=== web (Free): uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} (1)
web.1: up 2024/01/01 12:00:00 +0900 (~ 1m ago)
```

### ステップ2: ログを確認

```bash
heroku logs --tail --app blog-automation-api-prod
```

起動成功のログ例:
```
Starting uvicorn with app.main:app
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

エラーのログ例:
```
Error: ...
Traceback (most recent call last):
...
```

### ステップ3: アプリを再起動

```bash
heroku restart --app blog-automation-api-prod
```

### ステップ4: ヘルスチェック

```bash
curl https://blog-automation-api-prod-1077654888a6.herokuapp.com/health
```

期待されるレスポンス:
```json
{"status": "healthy"}
```

## 緊急時の対処法

### アプリが完全にダウンしている場合

1. **Herokuダッシュボードで確認**
   - https://dashboard.heroku.com/apps/blog-automation-api-prod
   - 「Metrics」タブでリソース使用状況を確認
   - 「Activity」タブで最近のデプロイやエラーを確認

2. **アプリを再起動**
   ```bash
   heroku restart --app blog-automation-api-prod
   ```

3. **最新のコードを再デプロイ**
   ```bash
   git push heroku main
   ```

## 参考

- Heroku トラブルシューティング: https://devcenter.heroku.com/articles/troubleshooting
- Heroku ログ: https://devcenter.heroku.com/articles/logging

