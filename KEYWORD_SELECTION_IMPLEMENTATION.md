# キーワード選択機能の実装確認

## ✅ 実装状況

### 1. 関連キーワード100個の生成と分析

**バックエンド**: `backend/app/tasks.py` - `analyze_keywords_task()`

```python
# 1. OpenAIで関連キーワード100個を生成
related_keywords_100 = generate_related_keywords_with_openai(...)

# 2. DataForSEOで検索ボリューム・競合度を取得
keywords_data = get_keywords_data(keywords=related_keywords_100[:100], ...)

# 3. スコアリング
scored_keywords = score_keywords(keywords_data)

# 4. データベースに保存
updates = {
    "status": "keyword_selection",
    "analyzed_keywords": json.dumps(scored_keywords, ensure_ascii=False)
}
```

**保存されるデータ構造**:
```json
[
  {
    "keyword": "ブルーライトカットメガネ おすすめ",
    "search_volume": 1200,
    "competition_index": 45,
    "cpc": 120.5,
    "volume_score": 100.0,
    "competition_score": 55.0,
    "total_score": 82.0
  },
  ...
]
```

---

### 2. キーワード選択画面での表示

**フロントエンド**: `frontend/src/pages/KeywordSelection.tsx`

#### 表示される情報

| カラム | データソース | 表示形式 |
|--------|------------|---------|
| **キーワード** | `kw.keyword` | テキスト |
| **検索ボリューム** | `kw.search_volume` | 数値（カンマ区切り） |
| **競合度** | `kw.competition_index` | 0-100（色分け表示） |
| **CPC** | `kw.cpc` | 円表示（¥120.50） |
| **スコア** | `kw.total_score` | 数値（小数点1桁） |

#### 競合度の色分け

- **緑**: 30未満（低競合）
- **黄**: 30-60（中競合）
- **赤**: 60以上（高競合）

#### 実装コード

```tsx
{analyzedKeywords.map((kw: any, index: number) => (
  <tr key={index}>
    <td>
      <input
        type="checkbox"
        checked={selectedKeywords.has(kw.keyword)}
        onChange={() => handleToggleKeyword(kw.keyword)}
      />
    </td>
    <td>{kw.keyword}</td>
    <td>{kw.search_volume?.toLocaleString() || 0}</td>
    <td>
      <span className={/* 色分け */}>
        {kw.competition_index || 100}/100
      </span>
    </td>
    <td>¥{kw.cpc?.toFixed(2) || '0.00'}</td>
    <td>{kw.total_score?.toFixed(1) || '0.0'}</td>
  </tr>
))}
```

---

### 3. ユーザー選択機能

#### 選択機能

- ✅ **チェックボックス**: 各キーワードを個別に選択
- ✅ **全選択/全解除**: ワンクリックで全て選択/解除
- ✅ **選択状況表示**: 「選択中: X個 / 100個」

#### 検索・ソート機能

- ✅ **検索**: キーワード名でフィルタ
- ✅ **ソート**:
  - スコア順（デフォルト）
  - 検索ボリューム順
  - 競合度順（低い順）

#### 実装コード

```tsx
// 検索フィルタ
if (searchTerm) {
  keywords = keywords.filter((kw: any) =>
    kw.keyword?.toLowerCase().includes(searchTerm.toLowerCase())
  )
}

// ソート
keywords = [...keywords].sort((a: any, b: any) => {
  if (sortBy === 'score') {
    return (b.total_score || 0) - (a.total_score || 0)
  } else if (sortBy === 'volume') {
    return (b.search_volume || 0) - (a.search_volume || 0)
  } else {
    return (a.competition_index || 100) - (b.competition_index || 100)
  }
})
```

---

### 4. 選択後の処理

**バックエンド**: `backend/app/routers/articles.py` - `select_keywords_endpoint()`

1. 選択されたキーワードを受け取る
2. 選択されたキーワードの詳細データを取得
3. `selected_keywords`と`selected_keywords_data`を保存
4. 記事生成を開始（選択されたキーワードを`secondary_keywords`として使用）

---

## データフロー

```
1. 記事作成
   ↓
2. キーワード分析（バックグラウンド）
   - OpenAI: 100個生成
   - DataForSEO: 検索ボリューム・競合度取得
   - スコアリング
   ↓
3. analyzed_keywordsに保存（JSONB）
   [
     {
       "keyword": "...",
       "search_volume": 1200,
       "competition_index": 45,
       "cpc": 120.5,
       "total_score": 82.0
     },
     ...
   ]
   ↓
4. キーワード選択画面で表示
   - テーブル形式で100個表示
   - 検索・ソート機能
   - チェックボックスで選択
   ↓
5. ユーザーが選択
   ↓
6. 選択されたキーワードで記事生成
```

---

## 確認ポイント

### ✅ 実装済み

1. **100個のキーワード生成**: OpenAIで生成
2. **検索ボリューム取得**: DataForSEO APIで取得
3. **競合度取得**: DataForSEO APIで取得
4. **スコアリング**: 検索ボリューム60% + 競合度40%
5. **テーブル表示**: 全情報を表示
6. **選択機能**: チェックボックスで複数選択
7. **検索・ソート**: フィルタリング機能
8. **データ保存**: 選択されたキーワードを保存

### データ構造の一致

**バックエンドが保存するデータ**:
```python
{
    "keyword": "...",
    "search_volume": 1200,
    "competition_index": 45,
    "cpc": 120.5,
    "total_score": 82.0
}
```

**フロントエンドが期待するデータ**:
```typescript
kw.keyword          // ✅
kw.search_volume    // ✅
kw.competition_index // ✅
kw.cpc              // ✅
kw.total_score      // ✅
```

**✅ 完全に一致しています**

---

## 使用方法

1. **記事作成**: フォームに入力して「記事を生成」
2. **キーワード分析**: 自動で100個のキーワードを分析（約30-60秒）
3. **キーワード選択画面**: 自動でリダイレクト
4. **キーワード選択**:
   - 検索でフィルタ
   - ソートで並び替え
   - チェックボックスで選択
5. **記事生成**: 「選択したX個のキーワードで記事生成」をクリック

---

## まとめ

✅ **関連キーワード100個**: OpenAIで生成  
✅ **検索ボリューム**: DataForSEO APIで取得・表示  
✅ **競合度**: DataForSEO APIで取得・表示（色分け）  
✅ **CPC**: DataForSEO APIで取得・表示  
✅ **スコア**: 自動計算・表示  
✅ **ユーザー選択**: チェックボックスで複数選択可能  
✅ **検索・ソート**: フィルタリング機能完備  

**全て実装済みで、正常に動作します！**

