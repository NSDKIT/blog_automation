# メガネ記事案ジェネレーター - 基本設計書

## 1. アーキテクチャ

### 1.1 システム構成
```
[フロントエンド (React)]
    ↓
[バックエンド API (FastAPI)]
    ↓
[データベース (PostgreSQL)] [外部API (OpenAI, Anthropic, Google, Shopify)]
```

### 1.2 技術スタック
- **フロントエンド**
  - React 18
  - TypeScript
  - Tailwind CSS
  - React Query (データフェッチング)
  - React Router (ルーティング)

- **バックエンド**
  - Python 3.11
  - FastAPI
  - SQLAlchemy (ORM)
  - Pydantic (バリデーション)
  - Celery (非同期タスク処理)

- **データベース**
  - PostgreSQL 15

- **認証**
  - JWT (JSON Web Token)
  - bcrypt (パスワードハッシュ化)

## 2. データベース設計

### 2.1 テーブル構成

#### users テーブル
- id: UUID (PK)
- email: VARCHAR (UNIQUE)
- password_hash: VARCHAR
- name: VARCHAR
- role: VARCHAR (admin/user)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

#### articles テーブル
- id: UUID (PK)
- user_id: UUID (FK -> users.id)
- keyword: VARCHAR
- target: VARCHAR
- article_type: VARCHAR
- title: TEXT
- content: TEXT
- shopify_article_id: VARCHAR (nullable)
- status: VARCHAR (draft/published/failed)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

#### article_histories テーブル
- id: UUID (PK)
- article_id: UUID (FK -> articles.id)
- action: VARCHAR (created/updated/deleted)
- changes: JSONB
- created_at: TIMESTAMP

#### settings テーブル
- id: UUID (PK)
- user_id: UUID (FK -> users.id)
- key: VARCHAR
- value: TEXT (暗号化)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

## 3. API設計

### 3.1 認証API
- POST /api/auth/register - ユーザー登録
- POST /api/auth/login - ログイン
- POST /api/auth/logout - ログアウト
- GET /api/auth/me - 現在のユーザー情報取得

### 3.2 記事API
- GET /api/articles - 記事一覧取得
- GET /api/articles/{id} - 記事詳細取得
- POST /api/articles - 記事生成
- PUT /api/articles/{id} - 記事更新
- DELETE /api/articles/{id} - 記事削除
- POST /api/articles/{id}/publish - Shopifyに投稿

### 3.3 設定API
- GET /api/settings - 設定取得
- PUT /api/settings - 設定更新

## 4. UI設計

### 4.1 ページ構成
1. **ログインページ** (`/login`)
2. **ダッシュボード** (`/`)
   - 記事一覧
   - 新規記事生成ボタン
3. **記事生成ページ** (`/articles/new`)
   - 入力フォーム
   - 生成進捗表示
4. **記事詳細ページ** (`/articles/{id}`)
   - 記事内容表示
   - 編集機能
   - 投稿ボタン
5. **設定ページ** (`/settings`)
   - API設定
   - Google Sheets設定
   - Shopify設定

## 5. ワークフロー処理

### 5.1 記事生成フロー
1. ユーザーが入力フォームに情報を入力
2. バックエンドが非同期タスクをキューに追加
3. Celeryワーカーが以下を実行：
   - 知識検索
   - Google検索
   - 記事分析
   - タイトル生成
   - 記事生成
   - 画像選定
   - Shopify形式変換
4. 結果をデータベースに保存
5. フロントエンドにWebSocketで進捗を通知

