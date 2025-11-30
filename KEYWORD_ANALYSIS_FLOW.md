# 「キーワードを分析」ボタンを押したときのコード実行フロー

## 1. フロントエンド（KeywordAnalysis.tsx）

### ボタンクリック時の処理

```typescript
// frontend/src/pages/KeywordAnalysis.tsx (163-169行目)
<button
  onClick={() => startAnalysisMutation.mutate(selectedArticleId)}
  disabled={startAnalysisMutation.isPending || isAnalyzing}
  className="..."
>
  {startAnalysisMutation.isPending ? '分析を開始中...' : 'キーワード分析を開始'}
</button>
```

### Mutationの定義

```typescript
// frontend/src/pages/KeywordAnalysis.tsx (34-43行目)
const startAnalysisMutation = useMutation({
  mutationFn: (articleId: string) => articlesApi.startKeywordAnalysis(articleId),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['article', selectedArticleId] })
    setIsAnalyzing(true)
  },
  onError: (error: any) => {
    alert(`キーワード分析の開始に失敗しました: ${error.response?.data?.detail || error.message}`)
  },
})
```

## 2. API呼び出し（articles.ts）

```typescript
// frontend/src/api/articles.ts (104-107行目)
startKeywordAnalysis: async (id: string) => {
  const response = await apiClient.post(`/articles/${id}/start-keyword-analysis`)
  return response.data
},
```

**実行されるHTTPリクエスト:**
```
POST /api/articles/{article_id}/start-keyword-analysis
```

## 3. バックエンドエンドポイント（articles.py）

### エンドポイント定義

```python
# backend/app/routers/articles.py (474-580行目)
@router.post(
    "/{article_id}/start-keyword-analysis",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def start_keyword_analysis_endpoint(
    article_id: UUID,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
```

### 実行される処理

1. **記事の存在確認** (492-498行目)
   ```python
   article = get_article_by_id(str(article_id), str(current_user.get("id")))
   if not article:
       raise HTTPException(status_code=404, detail="記事が見つかりません")
   ```

2. **ステータスチェック** (500-512行目)
   - 既に`keyword_selection`の場合はエラー
   - 既に`keyword_analysis`の場合はエラー

3. **記事データの準備** (514-523行目)
   ```python
   article_data = {
       "keyword": article.get("keyword"),
       "target": article.get("target"),
       "article_type": article.get("article_type"),
       "important_keyword1": None,
       "important_keyword2": None,
       "important_keyword3": None,
       "secondary_keywords": []
   }
   ```

4. **ステータスを`keyword_analysis`に更新** (525-541行目)
   ```python
   initial_progress = {
       "status_check": False,
       "openai_generation": False,
       "dataforseo_fetch": False,
       "scoring_completed": False,
       "current_step": "status_check",
       "error_message": None
   }
   update_article(
       str(article_id),
       str(current_user.get("id")),
       {
           "status": "keyword_analysis",
           "keyword_analysis_progress": json.dumps(initial_progress, ensure_ascii=False)
       }
   )
   ```

5. **バックグラウンドタスクの開始** (546-574行目)
   - 別スレッドで`analyze_keywords_task`を実行
   - FastAPIの`BackgroundTasks`にも追加

## 4. バックグラウンドタスク（tasks.py）

### analyze_keywords_task関数

```python
# backend/app/tasks.py (107-307行目)
def analyze_keywords_task(article_id: str, article_data: Dict, user_id: str = None):
```

### 実行される処理の流れ

1. **ステータスチェック** (115-125行目)
   - 記事の`status`が`keyword_analysis`であることを確認
   - 既に`keyword_selection`の場合はスキップ

2. **進捗の更新** (127-135行目)
   ```python
   progress["status_check"] = True
   progress["current_step"] = "openai_generation"
   update_article(article_id, user_id, {
       "keyword_analysis_progress": json.dumps(progress, ensure_ascii=False)
   })
   ```

3. **OpenAIで100個のキーワード生成** (137-150行目)
   ```python
   related_keywords = generate_related_keywords_with_openai(
       keyword=article_data["keyword"],
       user_id=user_id
   )
   progress["openai_generation"] = True
   progress["current_step"] = "dataforseo_fetch"
   ```

4. **DataForSEOでキーワードデータ取得** (152-180行目)
   ```python
   keywords_data = get_keywords_data(
       keywords=related_keywords[:100],
       location_code=2840,  # 日本
       language_code="ja",
       user_id=user_id
   )
   progress["dataforseo_fetch"] = True
   progress["current_step"] = "scoring"
   ```

5. **スコアリング** (182-220行目)
   ```python
   scored_keywords = score_keywords(keywords_data)
   # 上位20個のキーワードに対してGoogle Ads APIでより正確なデータを取得
   top_20_keywords = scored_keywords[:20]
   google_ads_data = get_keywords_data_google_ads(
       keywords=[kw["keyword"] for kw in top_20_keywords],
       location_code=2840,
       language_code="ja",
       user_id=user_id
   )
   # スコアを更新
   scored_keywords = update_scores_with_google_ads(scored_keywords, google_ads_data)
   progress["scoring_completed"] = True
   ```

6. **結果の保存** (222-240行目)
   ```python
   update_article(article_id, user_id, {
       "status": "keyword_selection",
       "analyzed_keywords": json.dumps(scored_keywords, ensure_ascii=False),
       "keyword_analysis_progress": json.dumps(progress, ensure_ascii=False)
   })
   ```

## 5. フロントエンドでのポーリング（KeywordAnalysis.tsx）

### 記事データの自動更新

```typescript
// frontend/src/pages/KeywordAnalysis.tsx (19-31行目)
const { data: selectedArticle } = useQuery({
  queryKey: ['article', selectedArticleId],
  queryFn: () => articlesApi.getArticle(selectedArticleId),
  enabled: !!selectedArticleId,
  refetchInterval: (query) => {
    const article = query.state.data
    // キーワード分析中の場合はポーリング
    if (article?.status === 'keyword_analysis') {
      return 2000 // 2秒ごとにポーリング
    }
    return false
  },
})
```

### 進捗の表示

```typescript
// frontend/src/pages/KeywordAnalysis.tsx (57-82行目)
const steps = [
  {
    key: 'status_check',
    label: '記事のstatusがkeyword_analysisであること',
    completed: progress.status_check || isKeywordAnalysis,
  },
  {
    key: 'openai_generation',
    label: 'OpenAIで100個のキーワード生成が成功すること',
    completed: progress.openai_generation || false,
  },
  {
    key: 'dataforseo_fetch',
    label: 'DataForSEOでキーワードデータ取得が成功すること',
    completed: progress.dataforseo_fetch || false,
  },
  {
    key: 'scoring_completed',
    label: 'スコアリングが完了すること',
    completed: progress.scoring_completed || false,
  },
]
```

## 6. 自動リダイレクト（KeywordAnalysis.tsx）

### 分析完了時の処理

```typescript
// frontend/src/pages/KeywordAnalysis.tsx (45-55行目)
const handleAnalysisComplete = () => {
  if (selectedArticle?.status === 'keyword_selection') {
    navigate(`/articles/${selectedArticleId}/keywords`)
  }
}

// キーワード分析が完了したら自動でリダイレクト
if (selectedArticle?.status === 'keyword_selection' && isAnalyzing) {
  handleAnalysisComplete()
}
```

## 実行順序のまとめ

1. **フロントエンド**: ボタンクリック → `startAnalysisMutation.mutate()`
2. **API呼び出し**: `POST /api/articles/{id}/start-keyword-analysis`
3. **バックエンド**: `start_keyword_analysis_endpoint()` 実行
   - 記事の存在確認
   - ステータスを`keyword_analysis`に更新
   - バックグラウンドタスクを開始
4. **バックグラウンドタスク**: `analyze_keywords_task()` 実行
   - OpenAIでキーワード生成
   - DataForSEOでデータ取得
   - スコアリング
   - ステータスを`keyword_selection`に更新
5. **フロントエンド**: ポーリングで進捗を確認（2秒ごと）
6. **フロントエンド**: 分析完了を検知 → 自動リダイレクト
7. **キーワード選択ページ**: `/articles/{id}/keywords` に遷移

