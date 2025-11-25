# Supabaseテーブル作成ガイド

## 手順

### 1. Supabaseプロジェクトにアクセス

1. https://supabase.com にログイン
2. プロジェクトを選択（または新規作成）

### 2. SQL Editorを開く

1. 左メニューから「SQL Editor」をクリック
2. 「New query」をクリック

### 3. SQLスクリプトを実行

1. `backend/supabase_tables.sql` の内容をコピー
2. SQL Editorに貼り付け
3. 「Run」ボタンをクリック（または Cmd/Ctrl + Enter）

### 4. テーブルの確認

1. 左メニューから「Table Editor」をクリック
2. 以下のテーブルが作成されていることを確認：
   - ✅ `users` - ユーザー管理
   - ✅ `articles` - 記事管理
   - ✅ `article_histories` - 記事履歴
   - ✅ `settings` - 設定管理
   - ✅ `knowledge_base` - 知識ベース
   - ✅ `images` - 画像管理

## 作成されるテーブル

### 1. users（ユーザー管理）
- ユーザーID、メールアドレス、パスワード、名前、権限
- 用途: ユーザー登録・ログイン

### 2. articles（記事管理）
- 記事ID、ユーザーID、キーワード、タイトル、内容、ステータス
- 用途: 生成された記事の保存

### 3. article_histories（記事履歴）
- 履歴ID、記事ID、アクション、変更内容
- 用途: 記事の変更履歴

### 4. settings（設定管理）
- 設定ID、ユーザーID、キー、値
- 用途: ユーザー設定の保存

### 5. knowledge_base（知識ベース）
- 知識ID、タイトル、内容、キーワード
- 用途: 眼鏡生産者の想いなどの知識

### 6. images（画像管理）
- 画像ID、URL、altテキスト、カテゴリ、キーワード
- 用途: 記事に挿入する画像

## Row Level Security (RLS)

すべてのテーブルにRLSが設定されています：

- **users**: 全ユーザーが読み取り可能、自分のデータのみ更新可能
- **articles**: 自分の記事のみアクセス可能
- **article_histories**: 自分の記事の履歴のみアクセス可能
- **settings**: 自分の設定のみアクセス可能
- **knowledge_base**: 全ユーザーが読み取り可能
- **images**: 全ユーザーが読み取り可能

## 接続情報の取得

### 1. Database接続文字列を取得

1. Supabaseダッシュボードの「Settings」→「Database」を開く
2. 「Connection string」セクションで「URI」を選択
3. 接続文字列をコピー（パスワード部分を実際のパスワードに置き換え）

例：
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

### 2. .envファイルに設定

```env
# Supabase PostgreSQL接続
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Supabase API
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

**注意**: `[YOUR-PASSWORD]` はSupabaseプロジェクト作成時に設定したデータベースパスワードです。

## サンプルデータ

SQLスクリプトには以下のサンプルデータが含まれています：

- **knowledge_base**: 5件の知識ベースデータ
- **images**: 3件の画像データ（URLは実際のものに置き換えてください）

## トラブルシューティング

### エラー: "extension uuid-ossp does not exist"

Supabaseでは通常、`uuid-ossp`の代わりに`gen_random_uuid()`を使用しますが、スクリプトでは`uuid_generate_v4()`を使用しています。エラーが出る場合は、SupabaseのデフォルトのUUID生成を使用するように変更してください。

### RLSエラー

アプリケーションからSupabaseに接続する場合、RLSが有効になっていると認証が必要です。開発中は一時的にRLSを無効化することもできますが、本番環境では有効にしておくことを推奨します。

### 接続エラー

- 接続文字列が正しいか確認
- データベースパスワードが正しいか確認
- ファイアウォール設定を確認（SupabaseのIPアドレスが許可されているか）

