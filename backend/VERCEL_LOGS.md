# Vercelでのサーバーログ確認方法

## 方法1: Vercelダッシュボードから確認（推奨）

### 手順

1. **Vercelダッシュボードにアクセス**
   - https://vercel.com/dashboard にアクセス
   - ログイン

2. **プロジェクトを選択**
   - デプロイしているプロジェクトをクリック

3. **デプロイメントを選択**
   - 最新のデプロイメントをクリック

4. **Functions タブを開く**
   - デプロイメント詳細ページで「Functions」タブをクリック
   - または、左側のメニューから「Functions」を選択

5. **ログを確認**
   - 各関数（APIエンドポイント）のログが表示されます
   - リアルタイムでログを確認できます

### リアルタイムログの確認

1. **デプロイメント詳細ページで「Logs」タブを開く**
   - リアルタイムでログストリームを確認できます

2. **フィルタリング**
   - 特定の関数やエラーのみを表示できます

## 方法2: Vercel CLIを使用

### インストール

```bash
# Vercel CLIをインストール（まだの場合）
npm i -g vercel

# または
brew install vercel-cli
```

### ログイン

```bash
vercel login
```

### ログの確認

```bash
# プロジェクトルートで実行
cd backend  # またはプロジェクトルート

# リアルタイムでログを確認
vercel logs --follow

# 最新のログを表示
vercel logs

# 特定のデプロイメントのログを確認
vercel logs [deployment-url]

# エラーのみを表示
vercel logs --follow | grep -i error
```

## 方法3: ブラウザの開発者ツールから確認

### ネットワークタブ

1. ブラウザの開発者ツールを開く（F12）
2. 「Network」タブを選択
3. 「記事を生成」ボタンを押す
4. APIリクエストをクリック
5. 「Response」タブでレスポンスを確認
6. 「Headers」タブでリクエスト/レスポンスヘッダーを確認

### コンソールタブ

フロントエンドのエラーやログを確認できます。

## 確認すべきログ

### 記事作成時のログ

Vercelのログで以下を探してください：

```
[create_article_endpoint] 記事作成開始
[create_article] 記事作成
[analyze_keywords_task] ========== 開始 ==========
```

### エラーログ

```
[analyze_keywords_task] エラー発生
ERROR
Exception
Traceback
```

## Vercel Functions のログ設定

### ログレベルの設定

Vercelでは、`print()`や`console.log()`の出力が自動的にログに記録されます。

### 構造化ログの推奨

より詳細なログを取得するために、以下のようにログを出力することを推奨します：

```python
import json
import sys

def log(message, level="INFO", data=None):
    """構造化ログを出力"""
    log_entry = {
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    print(json.dumps(log_entry), file=sys.stderr)
```

## トラブルシューティング

### ログが表示されない場合

1. **デプロイメントが最新か確認**
   - Vercelダッシュボードで最新のデプロイメントを確認

2. **関数が実行されているか確認**
   - Functions タブで関数が呼び出されているか確認

3. **環境変数が設定されているか確認**
   - Settings > Environment Variables で確認

### ログが多すぎる場合

1. **フィルタリングを使用**
   - Vercelダッシュボードでフィルタ機能を使用

2. **特定の関数のみを確認**
   - Functions タブで特定の関数を選択

## リアルタイムログの監視

### Vercelダッシュボード

1. プロジェクト > デプロイメント > 最新のデプロイメントを選択
2. 「Logs」タブを開く
3. リアルタイムでログストリームを確認

### コマンドライン

```bash
# リアルタイムでログを監視
vercel logs --follow
```

## ログのエクスポート

### Vercelダッシュボードから

1. デプロイメント詳細ページで「Logs」タブを開く
2. ログをコピーまたはスクリーンショットを撮る

### CLIから

```bash
# ログをファイルに保存
vercel logs > logs.txt

# 特定の期間のログを保存
vercel logs --since 1h > logs.txt
```

## 次のステップ

1. **Vercelダッシュボードでログを確認**
   - プロジェクト > 最新のデプロイメント > Logs タブ

2. **「記事を生成」ボタンを押す**
   - リアルタイムでログが表示されます

3. **以下のログを探す**
   - `[create_article_endpoint]` で始まるログ
   - `[analyze_keywords_task]` で始まるログ
   - `エラー`、`ERROR`、`Exception` を含むログ

4. **ログを共有**
   - スクリーンショットまたはログのテキストを共有してください

## 参考リンク

- [Vercel Logs Documentation](https://vercel.com/docs/observability/logs)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)

