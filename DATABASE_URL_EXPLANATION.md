# DATABASE_URLは必要ですか？

## 答え: **はい、必要です**

## 理由

このアプリケーションでは、**2つの異なる方法でSupabaseに接続**しています：

### 1. DATABASE_URL（SQLAlchemy経由）

**用途**: アプリケーションのデータ（users, articles, settings等）を保存・取得

**使用箇所**:
- `app/database.py` - SQLAlchemyでPostgreSQLに接続
- `app/routers/articles.py` - 記事のCRUD操作
- `app/routers/auth.py` - ユーザー認証
- `app/routers/settings.py` - 設定管理

**接続方法**:
```python
# app/database.py
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

**例**:
```python
# 記事を保存
article = Article(user_id=user.id, keyword="メガネ", ...)
db.add(article)
db.commit()  # ← DATABASE_URL経由でSupabase PostgreSQLに保存
```

---

### 2. SUPABASE_URL / SUPABASE_ANON_KEY（Supabaseクライアント経由）

**用途**: 知識ベースと画像データの取得

**使用箇所**:
- `app/supabase_client.py` - Supabaseクライアント
- `app/workflow.py` - 知識ベース検索、画像取得

**接続方法**:
```python
# app/supabase_client.py
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
```

**例**:
```python
# 知識ベースを検索
response = supabase.table("knowledge_base")\
    .select("*")\
    .ilike("content", f"%{keyword}%")\
    .execute()  # ← SUPABASE_URL経由でSupabase APIにアクセス
```

---

## なぜ2つ必要？

### DATABASE_URL（PostgreSQL直接接続）
- ✅ **SQLAlchemy ORM**を使用してデータを操作
- ✅ **トランザクション**管理が容易
- ✅ **リレーション**（users ↔ articles）を自動処理
- ✅ **マイグレーション**（Alembic）が使用可能

### SUPABASE_URL（Supabase API経由）
- ✅ **REST API**で簡単にアクセス
- ✅ **Row Level Security (RLS)**が自動適用
- ✅ **リアルタイム機能**が使用可能
- ✅ **認証機能**が統合されている

---

## Supabaseを使う場合の設定

### DATABASE_URL
SupabaseのPostgreSQL接続文字列を使用：

```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**取得方法**:
1. Supabaseダッシュボード → Settings → Database
2. Connection string → URI をコピー
3. `[PASSWORD]` を実際のパスワードに置き換え

### SUPABASE_URL / SUPABASE_ANON_KEY
SupabaseのAPI接続情報を使用：

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**取得方法**:
1. Supabaseダッシュボード → Settings → API
2. Project URL → `SUPABASE_URL`
3. anon public key → `SUPABASE_ANON_KEY`

---

## まとめ

| 接続方法 | 環境変数 | 用途 | 使用箇所 |
|---------|---------|------|---------|
| PostgreSQL直接接続 | `DATABASE_URL` | アプリデータ（users, articles等） | SQLAlchemy経由 |
| Supabase API | `SUPABASE_URL`<br>`SUPABASE_ANON_KEY` | 知識ベース、画像 | Supabaseクライアント経由 |

**結論**: 両方必要です。ただし、どちらも**同じSupabaseプロジェクト**に接続します。

---

## 設定例

```env
# Supabase PostgreSQL接続（SQLAlchemy用）
DATABASE_URL=postgresql://postgres:your-password@db.xxxxx.supabase.co:5432/postgres

# Supabase API接続（知識ベース・画像用）
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

両方とも同じSupabaseプロジェクトを指していますが、**接続方法が異なる**ため、両方の設定が必要です。

