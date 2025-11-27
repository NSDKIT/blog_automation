# Keywords Data API 分析と実装活用案

## 提供されたJSONファイルの分析

### 含まれているAPIエンドポイント

1. **`/v3/keywords_data/google_ads/search_volume/live`**
   - 検索ボリュームを取得
   - より正確なGoogle Ads APIベースのデータ

2. **`/v3/keywords_data/google_ads/keywords_for_site/live`**
   - 特定サイトで使用されているキーワードを取得
   - 競合サイト分析に有用

3. **`/v3/keywords_data/google_ads/keywords_for_keywords/live`**
   - キーワードから関連キーワードを取得
   - 現在の実装と類似の機能

4. **`/v3/keywords_data/google_trends/explore/live`**
   - Google Trendsデータを取得
   - トレンド分析に有用

5. **`/v3/keywords_data/dataforseo_trends/explore/live`**
   - DataForSEO独自のトレンドデータ
   - 過去のトレンド分析に有用

### 注意点

- 全てのレスポンスで`status_code: 40200 (Payment Required)`エラー
- アカウント残高不足またはAPIアクセス権限がない可能性
- 実際のデータ構造は確認できていない

---

## 現在の実装との比較

### 現在使用しているAPI

**`/v3/dataforseo_labs/google/keywords_for_keywords/live`**
- DataForSEO独自のデータベース
- より経済的
- 関連キーワード、検索ボリューム、競合度を取得

### 提供されたAPI（`keywords_data/google_ads`）

**`/v3/keywords_data/google_ads/keywords_for_keywords/live`**
- Google Ads APIベース（より正確）
- より高精度なデータ
- コストが高い可能性

---

## 実装への活用案

### 案1: より正確な検索ボリューム取得（推奨）

現在の`dataforseo_labs`に加えて、`keywords_data/google_ads/search_volume`を使用してより正確な検索ボリュームを取得

**メリット**:
- Google Ads APIベースでより正確
- 競合度データも取得可能

**実装方法**:
```python
async def get_keywords_data_google_ads(
    keywords: List[str],
    location_code: int = 2840,
    language_code: str = "ja",
    user_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Google Ads APIベースのKeywords Data APIで検索ボリュームを取得
    より正確なデータを提供
    """
    url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
    # 実装...
```

### 案2: 競合サイト分析

`keywords_for_site`を使用して競合サイトが使用しているキーワードを分析

**メリット**:
- 競合サイトのキーワード戦略を把握
- 記事に組み込むべきキーワードを発見

**実装方法**:
```python
async def get_keywords_for_site(
    target_domain: str,
    location_code: int = 2840,
    language_code: str = "ja",
    user_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    特定サイトで使用されているキーワードを取得
    競合サイト分析に使用
    """
    url = "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_site/live"
    # 実装...
```

### 案3: トレンド分析

Google Trends APIを使用してキーワードのトレンドを分析

**メリット**:
- 季節性のあるキーワードを発見
- トレンドが上昇中のキーワードを優先

**実装方法**:
```python
async def get_keyword_trends(
    keywords: List[str],
    location_code: int = 2840,
    user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Google Trendsデータを取得
    キーワードのトレンド分析に使用
    """
    url = "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live"
    # 実装...
```

---

## 推奨実装方針

### 優先度1: より正確な検索ボリューム取得

現在の`dataforseo_labs`に加えて、`keywords_data/google_ads/search_volume`を併用

**理由**:
- より正確な検索ボリュームデータ
- スコアリングの精度向上
- ユーザー選択時の判断材料が向上

**実装箇所**:
- `backend/app/dataforseo_client.py`に新関数を追加
- `backend/app/tasks.py`の`analyze_keywords_task`で併用

### 優先度2: 競合サイト分析

SERP分析で取得した上位サイトのキーワードを分析

**理由**:
- 競合が実際に使用しているキーワードを把握
- 記事に組み込むべきキーワードを発見

**実装箇所**:
- SERP分析後に、上位3-5サイトのキーワードを取得
- 記事生成プロンプトに追加

### 優先度3: トレンド分析

キーワードのトレンドデータを取得してスコアリングに反映

**理由**:
- 上昇トレンドのキーワードを優先
- 季節性のあるキーワードを考慮

**実装箇所**:
- キーワード分析時にトレンドデータを取得
- スコアリングにトレンドスコアを追加

---

## 実装例

### Google Ads APIベースの検索ボリューム取得

```python
async def get_keywords_data_google_ads(
    keywords: List[str],
    location_code: int = 2840,
    language_code: str = "ja",
    user_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Google Ads APIベースのKeywords Data APIで検索ボリュームを取得
    より正確なデータを提供
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    # 最大100キーワードまでバッチ処理
    keywords_batch = keywords[:100]
    
    payload = [{
        "keywords": keywords_batch,
        "location_code": location_code,
        "language_code": language_code,
        "sort_by": "relevance"
    }]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                if task.get("status_code") == 20000:
                    return task.get("result", [])
            return None
    except httpx.HTTPStatusError as e:
        raise Exception(f"DataForSEO Google Ads API エラー: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise Exception(f"キーワードデータ取得エラー: {str(e)}")
```

---

## データ構造の違い（想定）

### `dataforseo_labs` API
```json
{
  "keyword_info": {
    "keyword": "キーワード",
    "search_volume": 1000,
    "competition_index": 50,
    "cpc": 100.5
  }
}
```

### `keywords_data/google_ads` API（想定）
```json
{
  "keyword": "キーワード",
  "search_volume": 1000,
  "competition": "MEDIUM",
  "competition_index": 50,
  "cpc": 100.5,
  "monthly_searches": [
    {"year": 2024, "month": 1, "search_volume": 1000},
    ...
  ]
}
```

---

## コスト比較

### `dataforseo_labs`
- 約$0.01-0.02/キーワード
- より経済的

### `keywords_data/google_ads`
- 約$0.02-0.05/キーワード（想定）
- より高精度だが高コスト

---

## 推奨実装

### ハイブリッド方式

1. **まず`dataforseo_labs`で100個のキーワードを分析**
   - コストを抑えつつ広範囲に分析

2. **上位20個のキーワードを`google_ads`で再分析**
   - より正確なデータで最終選定

3. **スコアリングに両方のデータを活用**
   - `dataforseo_labs`: 初期スクリーニング
   - `google_ads`: 最終選定

これにより、コストを抑えつつ精度を向上できます。

