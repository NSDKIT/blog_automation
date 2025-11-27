# DataForSEO API 使用状況

## 現在実装で使用しているAPI

### 1. SERP API（検索エンジン結果ページAPI）

**エンドポイント**: `POST /v3/serp/google/organic/advanced/live`

**用途**: Google検索上位50件の結果を取得・分析

**実装箇所**: `backend/app/dataforseo_client.py` - `get_serp_data()`

**取得データ**:
- オーガニック検索結果50件（title, snippet, url, position）
- People Also Ask（PAA）の質問
- Related Searches（関連検索）
- Featured Snippets（特徴的なスニペット）

**使用タイミング**:
- 記事生成時に自動実行
- メインキーワードで検索

**パラメータ**:
- `keyword`: 検索キーワード
- `location_code`: 2840（日本）
- `language_code`: "ja"（日本語）
- `device`: "mobile" または "desktop"
- `depth`: 50（取得する結果数）
- `calculate_rectangles`: true（見出し構造を取得）
- `include_serp_info`: true

**コスト**: 約$0.05-0.10/リクエスト（depth=50の場合）

---

### 2. Keywords Data API（DataForSEO Labs）

**エンドポイント**: `POST /v3/dataforseo_labs/google/keywords_for_keywords/live`

**用途**: キーワードの検索ボリューム、競合度、関連キーワードを取得

**実装箇所**: `backend/app/dataforseo_client.py` - `get_keywords_data()`

**取得データ**:
- 検索ボリューム（月間検索数）
- 競合度（competition_index: 0-100）
- CPC（クリック単価）
- 関連キーワード（各キーワードの上位20件）

**使用タイミング**:
- キーワード分析時（100個のキーワードをバッチで取得）
- 記事生成時（メインキーワード + 重要キーワード）

**パラメータ**:
- `keywords`: キーワードリスト（最大100個）
- `location_code`: 2840（日本）
- `language_code`: "ja"（日本語）
- `include_serp_info`: true
- `limit`: 20（各キーワードの関連キーワード数）

**コスト**: 約$0.01-0.02/キーワード

**注意**: 100個のキーワードをバッチで送信可能

---

### 3. Content Generation API - メタタグ生成

**エンドポイント**: `POST /v3/content_generation/generate_meta_tags/live`

**用途**: SEO最適化されたメタタイトル・メタディスクリプションを生成

**実装箇所**: `backend/app/dataforseo_client.py` - `generate_meta_tags()`

**取得データ**:
- `meta_title`: SEO最適化されたメタタイトル（30-60文字）
- `meta_description`: SEO最適化されたメタディスクリプション（120-160文字）

**使用タイミング**:
- 記事生成後、タイトルと本文が完成した後

**パラメータ**:
- `text`: 記事本文（最大5000文字）
- `title`: 記事タイトル
- `meta_title_max_length`: 60
- `meta_description_max_length`: 160

**コスト**: 約$0.01/リクエスト

---

### 4. Content Generation API - サブトピック生成

**エンドポイント**: `POST /v3/content_generation/generate_subtopics/live`

**用途**: メインキーワードから関連サブトピックを10個生成

**実装箇所**: `backend/app/dataforseo_client.py` - `generate_subtopics()`

**取得データ**:
- サブトピックのリスト（最大10個）

**使用タイミング**:
- 記事生成時、メインキーワードからサブトピックを生成

**パラメータ**:
- `keyword`: メインキーワード
- `limit`: 10

**コスト**: 約$0.01/リクエスト

---

## API使用フロー

### 記事生成時のAPI呼び出し順序

```
1. キーワード分析フェーズ
   ↓
   OpenAIで関連キーワード100個を生成（AI API）
   ↓
   Keywords Data API（100個のキーワードをバッチで取得）
   ↓
   ユーザーがキーワードを選択
   
2. 記事生成フェーズ
   ↓
   SERP API（メインキーワードで上位50件を取得）
   ↓
   Content Generation API - サブトピック生成
   ↓
   AI APIでタイトル・記事生成（OpenAI/Gemini）
   ↓
   Content Generation API - メタタグ生成
```

---

## 使用していないAPI（提案書に記載あり）

以下のAPIは提案書に記載されていますが、**現在は実装していません**：

### 1. Domain Analytics API
- **用途**: 競合サイトの技術スタック分析
- **エンドポイント**: `/v3/domain_analytics/...`
- **理由**: 優先度が低いため未実装

### 2. Backlinks API
- **用途**: バックリンク分析
- **エンドポイント**: `/v3/backlinks/...`
- **理由**: 優先度が低いため未実装

### 3. OnPage API
- **用途**: 公開後のページ最適化チェック
- **エンドポイント**: `/v3/on_page/...`
- **理由**: 記事生成後の機能のため未実装

### 4. Content Analysis API
- **用途**: コンテンツの感情分析
- **エンドポイント**: `/v3/content_analysis/...`
- **理由**: 優先度が低いため未実装

### 5. Business Data API
- **用途**: Google My Business、Google Hotelsデータ
- **エンドポイント**: `/v3/business_data/...`
- **理由**: 眼鏡記事には不要のため未実装

### 6. App Data API
- **用途**: Google Play、App Storeデータ
- **エンドポイント**: `/v3/app_data/...`
- **理由**: 眼鏡記事には不要のため未実装

---

## APIコスト試算（1記事あたり）

### キーワード分析時
- Keywords Data API（100キーワード）: 約$1-2

### 記事生成時
- SERP API（depth=50）: 約$0.05-0.10
- Content Generation API（サブトピック）: 約$0.01
- Content Generation API（メタタグ）: 約$0.01

**合計**: 約$1.07-2.12/記事（約160-320円）

---

## API認証

### 認証方法
- **Basic認証**: `login:password`をBase64エンコード
- **ヘッダー**: `Authorization: Basic {encoded_credentials}`

### 設定方法
1. **環境変数**: `.env`ファイルに設定
   ```env
   DATAFORSEO_LOGIN=your_login
   DATAFORSEO_PASSWORD=your_password
   ```

2. **ユーザー設定**: 設定画面（`/settings`）で登録
   - `dataforseo_login`
   - `dataforseo_password`

---

## API制限

### レート制限
- **毎分最大2000回**のAPIコール
- 各POSTコールに最大100タスク

### バッチ処理
- Keywords Data API: 最大100キーワードまでバッチ送信可能
- SERP API: 1リクエストに1キーワード

---

## エラーハンドリング

### APIエラー時の動作
- **エラーログを出力**
- **記事生成は続行**（SEO分析なしで生成）
- エラーが発生しても記事生成は失敗しない

### よくあるエラー
1. **認証エラー**: DataForSEO設定が未完了
2. **クォータ超過**: レート制限に達した
3. **禁止カテゴリ**: 武器、タバコ、ドラッグ等のキーワード
4. **タイムアウト**: ネットワークエラー

---

## 今後の拡張予定

### 優先度: 高
- **OnPage API**: 公開後のページ最適化チェック
- **Content Analysis API**: コンテンツ品質チェック

### 優先度: 中
- **Backlinks API**: 競合の被リンク戦略分析
- **Domain Analytics API**: 競合サイトの技術分析

### 優先度: 低
- **Business Data API**: ローカルSEO対応
- **App Data API**: アプリ関連記事対応

