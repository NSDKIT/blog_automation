import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { articlesApi } from '../api/articles'
import { useState, useMemo } from 'react'

export default function KeywordSelection() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedKeywords, setSelectedKeywords] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'score' | 'volume' | 'competition'>('score')

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', id],
    queryFn: () => articlesApi.getArticle(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const article = query.state.data
      // keyword_analysisまたはkeyword_selectionの場合はポーリング
      if (article?.status === 'keyword_analysis' || article?.status === 'keyword_selection') {
        return 2000 // 2秒ごとにポーリング
      }
      // 記事作成直後（statusがまだ設定されていない場合）もポーリング
      if (!article?.status || article?.status === 'draft' || article?.status === 'processing') {
        return 2000
      }
      return false
    },
  })

  const selectKeywordsMutation = useMutation({
    mutationFn: (keywords: string[]) => articlesApi.selectKeywords(id!, keywords),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', id] })
      navigate(`/articles/${id}`)
    },
  })

  // 分析済みキーワードを取得
  const analyzedKeywords = useMemo(() => {
    if (!article?.analyzed_keywords) return []
    
    let keywords = article.analyzed_keywords
    if (typeof keywords === 'string') {
      try {
        keywords = JSON.parse(keywords)
      } catch {
        return []
      }
    }
    
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
    
    return keywords
  }, [article?.analyzed_keywords, searchTerm, sortBy])

  const handleToggleKeyword = (keyword: string) => {
    const newSelected = new Set(selectedKeywords)
    if (newSelected.has(keyword)) {
      newSelected.delete(keyword)
    } else {
      newSelected.add(keyword)
    }
    setSelectedKeywords(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedKeywords.size === analyzedKeywords.length) {
      setSelectedKeywords(new Set())
    } else {
      setSelectedKeywords(new Set(analyzedKeywords.map((kw: any) => kw.keyword)))
    }
  }

  const handleSubmit = () => {
    if (selectedKeywords.size === 0) {
      alert('少なくとも1つのキーワードを選択してください')
      return
    }
    selectKeywordsMutation.mutate(Array.from(selectedKeywords))
  }

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">キーワード分析中...</p>
        </div>
      </div>
    )
  }

  if (!article) {
    return <div className="text-center py-12">記事が見つかりません</div>
  }

  // キーワード分析中または記事作成直後の場合
  if (article.status === 'keyword_analysis' || !article.status || article.status === 'draft' || article.status === 'processing') {
    const progress = article.keyword_analysis_progress || {}
    const isKeywordAnalysis = article.status === 'keyword_analysis'
    
    // 進捗状況のチェックリスト
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
    
    const allCompleted = steps.every(step => step.completed)
    const currentStepIndex = steps.findIndex(step => !step.completed)
    const currentStep = currentStepIndex >= 0 ? steps[currentStepIndex] : null
    
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center mb-6">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <h1 className="text-2xl font-bold text-gray-900 mt-4 mb-2">キーワード分析中</h1>
            <p className="text-gray-600">
              関連キーワード100個を生成し、検索ボリューム・競合度を分析しています
            </p>
            {currentStep && (
              <p className="text-sm text-indigo-600 mt-2 font-semibold">
                現在のステップ: {currentStep.label}
              </p>
            )}
          </div>
          
          {/* 進捗状況の表示 */}
          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">進捗状況</h2>
            <div className="space-y-3">
              {steps.map((step) => (
                <div
                  key={step.key}
                  className={`flex items-center p-3 rounded-lg border ${
                    step.completed
                      ? 'bg-green-50 border-green-200'
                      : currentStep?.key === step.key
                      ? 'bg-yellow-50 border-yellow-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex-shrink-0 mr-3">
                    {step.completed ? (
                      <svg
                        className="w-6 h-6 text-green-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    ) : currentStep?.key === step.key ? (
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-600"></div>
                    ) : (
                      <svg
                        className="w-6 h-6 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <p
                      className={`text-sm font-medium ${
                        step.completed
                          ? 'text-green-900'
                          : currentStep?.key === step.key
                          ? 'text-yellow-900'
                          : 'text-gray-500'
                      }`}
                    >
                      {step.label}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            {/* エラーメッセージの表示 */}
            {progress.error_message && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm font-semibold text-red-900 mb-1">エラー</p>
                <p className="text-sm text-red-700">{progress.error_message}</p>
              </div>
            )}
            
            {/* 完了メッセージ */}
            {allCompleted && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-900">
                  すべての条件が満たされました。キーワード選択画面に移動します...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // keyword_selectionでもkeyword_analysisでもない場合（完了済みなど）
  if (article.status !== 'keyword_selection' && article.status !== 'keyword_analysis' && article.status !== 'draft' && article.status !== 'processing') {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <p className="text-gray-600">この記事は既に処理済みです（ステータス: {article.status}）</p>
          <button
            onClick={() => navigate(`/articles/${id}`)}
            className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
          >
            記事詳細に戻る
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">キーワード選択</h1>
          <p className="text-gray-600">
            メインキーワード: <span className="font-semibold">{article.keyword}</span>
          </p>
          <p className="text-sm text-gray-500 mt-1">
            記事に使用するキーワードを選択してください（複数選択可能）
          </p>
        </div>

        {/* 検索・ソート */}
        <div className="mb-4 flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="キーワードで検索..."
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div>
            <select
              className="border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
            >
              <option value="score">スコア順</option>
              <option value="volume">検索ボリューム順</option>
              <option value="competition">競合度順（低い順）</option>
            </select>
          </div>
          <button
            onClick={handleSelectAll}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
          >
            {selectedKeywords.size === analyzedKeywords.length ? '全て解除' : '全て選択'}
          </button>
        </div>

        {/* 選択状況 */}
        <div className="mb-4 p-3 bg-indigo-50 rounded-lg">
          <p className="text-sm font-semibold text-indigo-900">
            選択中: {selectedKeywords.size}個 / {analyzedKeywords.length}個
          </p>
        </div>

        {/* キーワードリスト */}
        <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                  <input
                    type="checkbox"
                    checked={selectedKeywords.size === analyzedKeywords.length && analyzedKeywords.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  キーワード
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  検索ボリューム
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  競合度
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPC
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  スコア
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analyzedKeywords.map((kw: any, index: number) => (
                <tr
                  key={index}
                  className={`hover:bg-gray-50 ${
                    selectedKeywords.has(kw.keyword) ? 'bg-indigo-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedKeywords.has(kw.keyword)}
                      onChange={() => handleToggleKeyword(kw.keyword)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{kw.keyword}</div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {kw.search_volume?.toLocaleString() || 0}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <span className={`font-semibold ${
                        (kw.competition_index || 100) < 30 ? 'text-green-600' :
                        (kw.competition_index || 100) < 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {kw.competition_index || 100}/100
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      ¥{kw.cpc?.toFixed(2) || '0.00'}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-semibold text-indigo-600">
                      {kw.total_score?.toFixed(1) || '0.0'}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* アクションボタン */}
        <div className="mt-6 flex justify-end gap-4">
          <button
            onClick={() => navigate(`/articles/${id}`)}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-md text-sm font-medium"
          >
            キャンセル
          </button>
          <button
            onClick={handleSubmit}
            disabled={selectedKeywords.size === 0 || selectKeywordsMutation.isPending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {selectKeywordsMutation.isPending
              ? '処理中...'
              : `選択した${selectedKeywords.size}個のキーワードで記事生成`}
          </button>
        </div>
      </div>
    </div>
  )
}

