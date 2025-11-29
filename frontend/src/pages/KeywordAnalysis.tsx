import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { articlesApi } from '../api/articles'
import { useNavigate } from 'react-router-dom'

export default function KeywordAnalysis() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedArticleId, setSelectedArticleId] = useState<string>('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // 記事一覧を取得
  const { data: articles, isLoading: articlesLoading } = useQuery({
    queryKey: ['articles'],
    queryFn: () => articlesApi.getArticles(),
  })

  // 選択された記事を取得
  const { data: selectedArticle, isLoading: articleLoading } = useQuery({
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

  // キーワード分析を開始
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

  // キーワード分析が完了したら、キーワード選択ページにリダイレクト
  const handleAnalysisComplete = () => {
    if (selectedArticle?.status === 'keyword_selection') {
      navigate(`/articles/${selectedArticleId}/keywords`)
    }
  }

  // キーワード分析が完了したら自動でリダイレクト
  if (selectedArticle?.status === 'keyword_selection' && isAnalyzing) {
    handleAnalysisComplete()
  }

  // キーワード分析中の進捗を表示
  const progress = selectedArticle?.keyword_analysis_progress || {}
  const isKeywordAnalysis = selectedArticle?.status === 'keyword_analysis'

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

  // キーワード分析可能な記事（draft状態、またはcompleted状態でanalyzed_keywordsがない記事）
  const analyzableArticles = articles?.filter(
    article => {
      // draft状態の記事
      if (article.status === 'draft') return true
      // completed状態でanalyzed_keywordsがない記事
      if (article.status === 'completed' && !article.analyzed_keywords) return true
      return false
    }
  ) || []

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">キーワード分析</h1>

        {/* 記事選択セクション */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            分析する記事を選択
          </label>
          <select
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={selectedArticleId}
            onChange={(e) => {
              setSelectedArticleId(e.target.value)
              setIsAnalyzing(false)
            }}
            disabled={isAnalyzing}
          >
            <option value="">記事を選択してください</option>
            {analyzableArticles.map((article) => (
              <option key={article.id} value={article.id}>
                {article.keyword} ({article.status})
              </option>
            ))}
          </select>
          {articlesLoading && <p className="mt-2 text-sm text-gray-500">記事一覧を読み込み中...</p>}
        </div>

        {/* 選択された記事の情報 */}
        {selectedArticle && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">選択された記事</h2>
            <div className="text-sm text-gray-600">
              <p>キーワード: {selectedArticle.keyword}</p>
              <p>ターゲット: {selectedArticle.target}</p>
              <p>種類: {selectedArticle.article_type}</p>
              <p>ステータス: {selectedArticle.status}</p>
            </div>
          </div>
        )}

        {/* キーワード分析開始ボタン */}
        {selectedArticleId && selectedArticle && (
          <div className="mb-6">
            {selectedArticle.status === 'keyword_analysis' ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  キーワード分析が進行中です。完了までお待ちください。
                </p>
              </div>
            ) : selectedArticle.status === 'keyword_selection' ? (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800 mb-4">
                  キーワード分析が完了しました。キーワード選択画面に移動します。
                </p>
                <button
                  onClick={() => navigate(`/articles/${selectedArticleId}/keywords`)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium"
                >
                  キーワード選択画面へ
                </button>
              </div>
            ) : (
              <button
                onClick={() => startAnalysisMutation.mutate(selectedArticleId)}
                disabled={startAnalysisMutation.isPending || isAnalyzing}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {startAnalysisMutation.isPending ? '分析を開始中...' : 'キーワード分析を開始'}
              </button>
            )}
          </div>
        )}

        {/* キーワード分析中の進捗表示 */}
        {selectedArticle && (selectedArticle.status === 'keyword_analysis' || isAnalyzing) && (
          <div className="border-t pt-6">
            <div className="text-center mb-6">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <h2 className="text-xl font-bold text-gray-900 mt-4 mb-2">キーワード分析中</h2>
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
        )}

        {/* 記事が選択されていない場合のメッセージ */}
        {!selectedArticleId && (
          <div className="text-center py-12 text-gray-500">
            <p>分析する記事を選択してください</p>
          </div>
        )}
      </div>
    </div>
  )
}

