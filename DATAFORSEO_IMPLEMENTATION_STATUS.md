# DataForSEO API 実装状況まとめ

## 提供されたJSONファイル（keyworddataapi_results.json）との比較

### JSONファイルに含まれているAPIエンドポイント

1. ✅ `/v3/keywords_data/google_ads/search_volume/live` - **実装済み**
2. ❌ `/v3/keywords_data/google_ads/keywords_for_site/live` - **未実装**
3. ❌ `/v3/keywords_data/google_ads/keywords_for_keywords/live` - **未実装**（代替として`dataforseo_labs`を使用）
4. ❌ `/v3/keywords_data/google_trends/explore/live` - **未実装**
5. ❌ `/v3/keywords_data/dataforseo_trends/explore/live` - **未実装**

---

## 現在実装されているAPI

### 1. ✅ SERP API
**エンドポイント**: `POST /v3/serp/google/organic/advanced/live`

**実装関数**: `get_serp_data()`

**用途**: Google検索上位50件の結果を取得・分析

**実装状況**: ✅ 完全実装済み

**エラーハンドリング**: ✅ 実装済み（status_codeチェック、Payment Required対応）

---

### 2. ✅ Keywords Data API (DataForSEO Labs)
**エンドポイント**: `POST /v3/dataforseo_labs/google/keywords_for_keywords/live`

**実装関数**: `get_keywords_data()`

**用途**: キーワードの検索ボリューム、競合度、関連キーワードを取得

**実装状況**: ✅ 完全実装済み

**注意**: JSONファイルの`/v3/keywords_data/google_ads/keywords_for_keywords/live`とは異なるAPIを使用

**エラーハンドリング**: ✅ 実装済み

---

### 3. ✅ Google Ads API - Search Volume
**エンドポイント**: `POST /v3/keywords_data/google_ads/search_volume/live`

**実装関数**: `get_keywords_data_google_ads()`

**用途**: Google Ads APIベースでより正確な検索ボリュームを取得

**実装状況**: ✅ 完全実装済み（ハイブリッド方式で使用）

**使用タイミング**: 上位20個のキーワードを再分析する際に使用

**エラーハンドリング**: ✅ 実装済み（Payment Requiredエラーを検出）

---

### 4. ✅ Content Generation API - Meta Tags
**エンドポイント**: `POST /v3/content_generation/generate_meta_tags/live`

**実装関数**: `generate_meta_tags()`

**用途**: SEO最適化されたメタタイトル・メタディスクリプションを生成

**実装状況**: ✅ 完全実装済み

**エラーハンドリング**: ✅ 実装済み

---

### 5. ✅ Content Generation API - Subtopics
**エンドポイント**: `POST /v3/content_generation/generate_subtopics/live`

**実装関数**: `generate_subtopics()`

**用途**: メインキーワードから関連サブトピックを10個生成

**実装状況**: ✅ 完全実装済み

**エラーハンドリング**: ✅ 実装済み

---

## 未実装のAPI（JSONファイルに含まれているが実装していない）

### 1. ❌ Google Ads API - Keywords for Site
**エンドポイント**: `POST /v3/keywords_data/google_ads/keywords_for_site/live`

**用途**: 特定サイトで使用されているキーワードを取得（競合サイト分析）

**実装状況**: ❌ 未実装

**提案**: 競合サイト分析機能として実装可能

**優先度**: 中

---

### 2. ❌ Google Ads API - Keywords for Keywords
**エンドポイント**: `POST /v3/keywords_data/google_ads/keywords_for_keywords/live`

**用途**: キーワードから関連キーワードを取得（Google Ads APIベース）

**実装状況**: ❌ 未実装

**注意**: 現在は`/v3/dataforseo_labs/google/keywords_for_keywords/live`を使用

**提案**: より正確なデータが必要な場合に実装可能

**優先度**: 低（現在の`dataforseo_labs`で十分）

---

### 3. ❌ Google Trends API
**エンドポイント**: `POST /v3/keywords_data/google_trends/explore/live`

**用途**: Google Trendsデータを取得（トレンド分析）

**実装状況**: ❌ 未実装

**提案**: キーワードのトレンド分析機能として実装可能

**優先度**: 中

---

### 4. ❌ DataForSEO Trends API
**エンドポイント**: `POST /v3/keywords_data/dataforseo_trends/explore/live`

**用途**: DataForSEO独自のトレンドデータを取得

**実装状況**: ❌ 未実装

**提案**: 過去のトレンド分析機能として実装可能

**優先度**: 低

---

## 実装の違い

### JSONファイルのAPI vs 現在の実装

| JSONファイルのAPI | 現在の実装 | 理由 |
|------------------|-----------|------|
| `/v3/keywords_data/google_ads/keywords_for_keywords/live` | `/v3/dataforseo_labs/google/keywords_for_keywords/live` | コスト効率のため（dataforseo_labsの方が安い） |
| `/v3/keywords_data/google_ads/search_volume/live` | ✅ 実装済み | ハイブリッド方式で使用（上位20個のみ） |

---

## 現在の実装アーキテクチャ

### ハイブリッド方式

```
1. dataforseo_labs API
   ↓ 100個のキーワードを広く分析（コスト抑制）
   
2. 初期スコアリング
   ↓
   
3. Google Ads API (search_volume)
   ↓ 上位20個のキーワードを再分析（より正確）
   
4. スコア再計算・再ソート
```

### 使用しているAPI

1. **SERP API**: 競合50件を分析
2. **DataForSEO Labs API**: 100個のキーワードを分析
3. **Google Ads API (search_volume)**: 上位20個を再分析
4. **Content Generation API**: メタタグ・サブトピック生成

---

## エラーハンドリング

### 実装済みのエラーハンドリング

✅ **全API関数で実装済み**:
- `status_code`チェック
- Payment Required (40200) エラーの検出
- 詳細なエラーメッセージ
- HTTPエラーの検出
- リクエストエラーの検出

### エラーメッセージの例

```python
# Payment Required
"Google Ads APIへのアクセス権限がありません（Payment Required）。
DataForSEOアカウントに残高があるか、Google Ads APIへのアクセス権限があるか確認してください。"

# その他のエラー
"DataForSEO Keywords API エラー (status_code: 40001): Invalid keyword format"
```

---

## 実装ファイル

### バックエンド

- ✅ `backend/app/dataforseo_client.py`: 全API関数を実装
- ✅ `backend/app/tasks.py`: ハイブリッド方式を実装
- ✅ `backend/app/workflow.py`: 記事生成時にAPIを呼び出し

---

## まとめ

### 実装済み（5個）

1. ✅ SERP API
2. ✅ Keywords Data API (DataForSEO Labs)
3. ✅ Google Ads API (Search Volume)
4. ✅ Content Generation API (Meta Tags)
5. ✅ Content Generation API (Subtopics)

### 未実装（4個）

1. ❌ Google Ads API (Keywords for Site) - 競合サイト分析
2. ❌ Google Ads API (Keywords for Keywords) - 代替APIを使用中
3. ❌ Google Trends API - トレンド分析
4. ❌ DataForSEO Trends API - トレンド分析

### 実装方針

- **コスト効率**: `dataforseo_labs`を優先使用
- **精度向上**: 上位キーワードのみ`google_ads`で再分析
- **エラーハンドリング**: 全APIで実装済み
- **フォールバック**: Google Ads APIが失敗しても`dataforseo_labs`で続行

---

## 今後の拡張案

### 優先度: 高

1. **Google Trends API**: トレンド分析機能
2. **Keywords for Site API**: 競合サイト分析機能

### 優先度: 中

1. **DataForSEO Trends API**: 過去のトレンド分析

### 優先度: 低

1. **Google Ads Keywords for Keywords**: 現在の`dataforseo_labs`で十分

