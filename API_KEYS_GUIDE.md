# APIキーの用途と取得方法

## 各APIキーの用途

### 1. OPENAI_API_KEY (必須)

**用途**: 
- **タイトル生成**: 記事のタイトルを生成（GPT-4oを使用）
- **画像挿入**: 生成された記事に適切な位置に画像を挿入（GPT-4oを使用）

**使用箇所**:
- `workflow.py` の `_generate_title()` メソッド
- `workflow.py` の `_insert_images()` メソッド

**取得方法**:
1. https://platform.openai.com/api-keys にアクセス
2. アカウントを作成/ログイン
3. "Create new secret key"をクリック
4. キーをコピー（`sk-`で始まる文字列）

**料金**: 使用量に応じて課金（GPT-4oは比較的高額）

---

### 2. ANTHROPIC_API_KEY (必須)

**用途**:
- **記事内容生成**: タイトルに基づいて記事本文を生成（Claude 3.5 Sonnetを使用）

**使用箇所**:
- `workflow.py` の `_generate_content()` メソッド

**取得方法**:
1. https://console.anthropic.com/ にアクセス
2. アカウントを作成/ログイン
3. "API Keys"から新しいキーを作成
4. キーをコピー（`sk-ant-`で始まる文字列）

**料金**: 使用量に応じて課金（Claude 3.5 Sonnetは中程度）

---

### 3. GEMINI_API_KEY (必須)

**用途**:
- **記事分析**: Google検索で取得した記事を分析し、最適文字数や頻出ワードを抽出
- **Shopify形式変換**: 生成された記事をShopifyのJSON形式に変換

**使用箇所**:
- `workflow.py` の `_analyze_articles()` メソッド
- `workflow.py` の `_convert_to_shopify()` メソッド

**取得方法**:
1. https://makersuite.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. "Create API Key"をクリック
4. キーをコピー

**料金**: 無料枠あり、使用量に応じて課金（比較的安価）

---

### 4. GOOGLE_API_KEY (必須)

**用途**:
- **Google検索**: キーワードでGoogle検索を実行し、上位記事のURLを取得

**使用箇所**:
- `workflow.py` の `_google_search()` メソッド

**取得方法**:
1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを作成（または既存のプロジェクトを選択）
3. "APIとサービス" → "認証情報" に移動
4. "認証情報を作成" → "APIキー" を選択
5. キーをコピー
6. **重要**: "Custom Search API"を有効化する必要があります
   - "APIとサービス" → "ライブラリ" → "Custom Search API" を検索して有効化

**料金**: 1日100回まで無料、それ以上は有料

---

### 5. GOOGLE_CSE_ID (必須)

**用途**:
- **Google検索エンジンID**: Custom Search APIで使用する検索エンジンのID

**使用箇所**:
- `workflow.py` の `_google_search()` メソッド（GOOGLE_API_KEYと一緒に使用）

**取得方法**:
1. https://programmablesearchengine.google.com/ にアクセス
2. "新しい検索エンジンを追加"をクリック
3. 検索対象を設定（例: インターネット全体）
4. 検索エンジンを作成
5. 作成した検索エンジンの設定画面で "検索エンジンID" をコピー

**料金**: 無料

---

### 6. SUPABASE_URL / SUPABASE_ANON_KEY (オプション - 後で設定)

**用途**:
- **知識ベース検索**: 眼鏡生産者の想いなどの知識を取得
- **画像管理**: 記事に挿入する画像を取得

**使用箇所**:
- `workflow.py` の `_knowledge_retrieval()` メソッド
- `workflow.py` の `_select_images()` メソッド

**取得方法**:
1. https://supabase.com にアクセス
2. プロジェクトを作成
3. プロジェクト設定 → API から取得
   - `Project URL` → `SUPABASE_URL`
   - `anon public` キー → `SUPABASE_ANON_KEY`

**料金**: 無料枠あり

**注意**: 未設定でも動作しますが、知識ベースと画像は空になります

---

### 7. SHOPIFY_* (オプション - 後で設定)

**用途**:
- **Shopify投稿**: 生成された記事をShopifyブログに自動投稿

**使用箇所**:
- `workflow.py` の `_convert_to_shopify()` メソッドの後
- `routers/articles.py` の `publish_article()` エンドポイント

**取得方法**:
1. Shopifyストアにログイン
2. 設定 → API → プライベートアプリを作成
3. アクセストークンを取得
4. ブログIDを取得（URLから確認可能）

**料金**: Shopifyプランによる

**注意**: 未設定でも記事生成は動作しますが、Shopifyへの投稿はできません

---

## 優先順位

### 必須（記事生成に最低限必要）:
1. ✅ **OPENAI_API_KEY** - タイトル生成
2. ✅ **ANTHROPIC_API_KEY** - 記事本文生成
3. ✅ **GEMINI_API_KEY** - 記事分析・変換
4. ✅ **GOOGLE_API_KEY** - Google検索
5. ✅ **GOOGLE_CSE_ID** - Google検索エンジン

### オプション（後で設定可能）:
6. ⚠️ **SUPABASE_URL / SUPABASE_ANON_KEY** - 知識ベース・画像（未設定でも動作）
7. ⚠️ **SHOPIFY_*** - Shopify投稿（未設定でも動作）

---

## 料金の目安（月額）

- **OpenAI GPT-4o**: 約$5-30/1000記事（使用量による）
- **Anthropic Claude 3.5 Sonnet**: 約$3-15/1000記事
- **Google Gemini**: 約$0-5/1000記事（無料枠あり）
- **Google Custom Search**: 無料枠あり（1日100回まで）
- **Supabase**: 無料枠あり
- **Shopify**: プランによる

---

## テスト用の最小構成

動作確認のみの場合、以下のAPIキーがあれば最低限動作します：

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
```

SupabaseとShopifyは後で設定可能です。

