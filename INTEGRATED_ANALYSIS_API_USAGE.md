# 統合分析で使用しているAPI一覧

## 現在の統合分析で使用しているAPI

### 1. メインキーワード分析
- **`keywords_data/google_ads/search_volume/live`**
  - 検索ボリューム、CPC、競合度を取得

### 2. メインキーワードの難易度
- **`dataforseo_labs/google/bulk_keyword_difficulty/live`**
  - キーワード難易度を取得

### 3. 関連キーワード取得
- **`dataforseo_labs/google/related_keywords/live`**
  - 関連キーワードを取得（デフォルト50件）

### 4. 関連キーワードの詳細データ
- **`dataforseo_labs/google/bulk_keyword_difficulty/live`**
  - 各関連キーワードの難易度を一括取得
- **`keywords_data/google_ads/search_volume/live`**
  - 各関連キーワードの検索ボリューム、CPC、競合度を取得

---

## 他の分析タブで使用しているAPI（統合分析では未使用）

### KeywordDataAnalysisタブで使用
- ❌ `keywords_data/google_ads/keywords_for_site/live` - サイト向けキーワード
- ❌ `keywords_data/google_ads/keywords_for_keywords/live` - キーワード向けキーワード
- ❌ `keywords_data/google_trends/explore/live` - Googleトレンド分析
- ❌ `keywords_data/dataforseo_trends/explore/live` - DataForSEOトレンド分析

### SERPAnalysisタブで使用
- ❌ `serp/google/organic/live/advanced` - SERP（検索結果ページ）分析

### DomainAnalyticsタブで使用
- ❌ `dataforseo_labs/google/keyword_suggestions/live` - キーワード提案
- ❌ `dataforseo_labs/google/keyword_ideas/live` - キーワードアイデア
- ❌ `dataforseo_labs/google/keywords_for_site/live` - サイト向けキーワード

---

## まとめ

**統合分析で使用しているAPI: 3種類**
1. `keywords_data/google_ads/search_volume/live` (2回使用: メイン + 関連キーワード)
2. `dataforseo_labs/google/related_keywords/live` (1回使用)
3. `dataforseo_labs/google/bulk_keyword_difficulty/live` (2回使用: メイン + 関連キーワード)

**統合分析で未使用のAPI: 8種類以上**
- KeywordDataAnalysisタブのAPI: 4種類
- SERPAnalysisタブのAPI: 1種類
- DomainAnalyticsタブのAPI: 3種類

---

## 改善提案

統合分析をより包括的にするために、以下のAPIを追加検討できます：

1. **SERP分析の追加**: 検索結果ページの構造分析
2. **トレンド分析の追加**: Google Trends / DataForSEO Trends
3. **キーワード提案の追加**: keyword_suggestions, keyword_ideas
4. **サイト向けキーワードの追加**: keywords_for_site（ターゲットサイトがある場合）

