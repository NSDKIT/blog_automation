# メガネ記事案ジェネレーター - プロジェクト概要

## 概要

`メガネ記事案ジェネレーター.yml`（Difyワークフロー）を商用展開可能なWebアプリケーションに変換しました。

## 実装内容

### 1. 要件定義・設計
- ✅ `requirements.md` - 要件定義書
- ✅ `design.md` - 基本設計書

### 2. バックエンド（Python + FastAPI）
- ✅ ユーザー認証・認可（JWT）
- ✅ 記事管理API
- ✅ 設定管理API
- ✅ データベースモデル（PostgreSQL）
- ✅ 記事生成ワークフロー（元のYAMLのロジックを移植）
- ✅ 非同期タスク処理（Celery対応準備）

### 3. フロントエンド（React + TypeScript）
- ✅ ログイン・登録ページ
- ✅ ダッシュボード（記事一覧）
- ✅ 記事生成ページ
- ✅ 記事詳細・編集ページ
- ✅ 設定ページ
- ✅ 認証状態管理（Zustand）

### 4. インフラストラクチャ
- ✅ Docker Compose設定
- ✅ データベースマイグレーション（Alembic）
- ✅ 環境変数管理

## 主な機能

### 記事生成ワークフロー
1. 知識ベース検索（眼鏡生産者の想い）
2. Google検索（キーワードで上位記事を取得）
3. 記事分析（最適文字数、頻出ワード抽出）
4. タイトル生成（GPT-4o）
5. 記事生成（Claude 3.5 Sonnet）
6. 画像選定（Google Sheetsから取得）
7. 画像挿入（GPT-4o）
8. Shopify形式変換（Gemini 2.0 Flash）
9. Shopify投稿

### ユーザー機能
- ユーザー登録・ログイン
- 記事の生成・編集・削除
- 記事履歴管理
- 設定管理（APIキー等）

## 技術スタック

### バックエンド
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT認証
- OpenAI API
- Anthropic API
- Google Gemini API
- Google Custom Search API
- Shopify API

### フロントエンド
- React 18
- TypeScript
- Tailwind CSS
- React Query
- React Router
- Zustand
- Axios

### インフラ
- Docker
- Docker Compose
- Alembic（マイグレーション）

## セットアップ手順

### 1. 環境変数の設定
```bash
cd backend
cp .env.example .env
# .envファイルを編集
```

### 2. Docker Composeで起動
```bash
docker-compose up -d
```

### 3. データベースマイグレーション
```bash
docker-compose exec backend alembic upgrade head
```

### 4. アクセス
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## 次のステップ

### 実装が必要な機能
1. **知識ベース検索の実装**
   - Dify APIとの連携
   - またはベクトルDBの実装

2. **Google Sheets連携の完成**
   - OAuth認証
   - 画像データの取得処理

3. **Shopify投稿の実装**
   - Shopify APIとの連携
   - エラーハンドリング

4. **Celeryワーカーの実装**
   - Redis連携
   - 非同期タスク処理
   - 進捗通知（WebSocket）

5. **エラーハンドリングの強化**
   - リトライ機能
   - エラーログ
   - ユーザーへの通知

6. **テストの追加**
   - ユニットテスト
   - 統合テスト
   - E2Eテスト

7. **セキュリティの強化**
   - 設定値の暗号化
   - レート制限
   - 入力検証の強化

## ファイル構成

```
記事生成/
├── backend/              # バックエンド
│   ├── app/
│   │   ├── routers/     # APIルーター
│   │   ├── models.py    # データベースモデル
│   │   ├── schemas.py   # Pydanticスキーマ
│   │   ├── workflow.py  # 記事生成ワークフロー
│   │   └── ...
│   ├── alembic/         # マイグレーション
│   └── requirements.txt
├── frontend/            # フロントエンド
│   ├── src/
│   │   ├── pages/       # ページコンポーネント
│   │   ├── components/  # 共通コンポーネント
│   │   ├── api/         # APIクライアント
│   │   └── store/       # 状態管理
│   └── package.json
├── docker-compose.yml   # Docker Compose設定
├── requirements.md     # 要件定義
├── design.md           # 基本設計
└── README.md           # プロジェクト説明
```

## 注意事項

- 本番環境では、環境変数を安全に管理してください
- APIキーは絶対にコミットしないでください
- データベースのバックアップを定期的に取得してください
- セキュリティアップデートを定期的に確認してください

## ライセンス

MIT

