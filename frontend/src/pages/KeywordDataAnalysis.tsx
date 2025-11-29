import { useState, useMemo } from 'react'
import { useMutation } from '@tanstack/react-query'
import apiClient from '../api/client'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'

interface KeywordDataResult {
  keyword: string
  location_code: number
  results: {
    [key: string]: {
      url: string
      payload: string
      headers?: { [key: string]: string }
      response_text?: string
      response_json?: any
      http_status_code?: number
      error?: string
    }
  }
  seo_analysis?: {
    keyword_data: {
      keyword: string
      search_volume: number
      competition_index: number
      competition: string
      cpc: number
      monthly_searches?: Array<{
        year: number
        month: number
        search_volume: number
      }>
    }
    scores: {
      volume_score: number
      competition_score: number
      cpc_score: number
      total_score: number
    }
    roi_metrics: {
      monthly_clicks: number
      monthly_ad_cost: number
      yearly_ad_cost: number
      monthly_seo_traffic: number
      cpc: number
    }
    alerts: Array<{
      type: 'warning' | 'info' | 'success'
      message: string
    }>
    related_keywords: Array<any>
  }
}

export default function KeywordDataAnalysis() {
  const [keyword, setKeyword] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [result, setResult] = useState<KeywordDataResult | null>(null)

  const analyzeMutation = useMutation({
    mutationFn: async (data: { keyword: string; location_code: number }) => {
      const response = await apiClient.post<KeywordDataResult>(
        `/keyword-data/analyze?keyword=${encodeURIComponent(data.keyword)}&location_code=${data.location_code}`,
        {}
      )
      return response.data
    },
    onSuccess: (data) => {
      setResult(data)
    },
    onError: (error: any) => {
      alert(`キーワード分析に失敗しました: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyword.trim()) {
      alert('キーワードを入力してください')
      return
    }
    analyzeMutation.mutate({ keyword: keyword.trim(), location_code: locationCode })
  }

  // 月次トレンドデータを準備
  const monthlyTrendData = useMemo(() => {
    if (!result?.seo_analysis?.keyword_data?.monthly_searches) return []
    
    return result.seo_analysis.keyword_data.monthly_searches
      .map(item => ({
        date: `${item.year}-${String(item.month).padStart(2, '0')}`,
        volume: item.search_volume,
        month: item.month
      }))
      .reverse()
  }, [result])

  // スコアデータを準備
  const scoreData = useMemo(() => {
    if (!result?.seo_analysis?.scores) return []
    
    const { scores } = result.seo_analysis
    return [
      { name: '検索ボリューム', score: scores.volume_score, color: '#3b82f6' },
      { name: '競合度', score: scores.competition_score, color: '#10b981' },
      { name: 'CPC効率', score: scores.cpc_score, color: '#f59e0b' },
    ]
  }, [result])

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">キーワードデータ分析</h1>

        {/* 入力フォーム */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
                キーワード
              </label>
              <input
                type="text"
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="例: weather forecast"
                required
              />
            </div>
            <div>
              <label htmlFor="location_code" className="block text-sm font-medium text-gray-700 mb-2">
                地域コード
              </label>
              <input
                type="number"
                id="location_code"
                value={locationCode}
                onChange={(e) => setLocationCode(parseInt(e.target.value) || 2840)}
                className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="2840 (日本)"
              />
              <p className="mt-1 text-xs text-gray-500">2840 = 日本, 2392 = アメリカ</p>
            </div>
          </div>
          <div className="mt-4">
            <button
              type="submit"
              disabled={analyzeMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analyzeMutation.isPending ? '分析中...' : '分析を実行'}
            </button>
          </div>
        </form>

        {/* SEO分析結果 */}
        {result?.seo_analysis && (
          <div className="mt-6 space-y-6">
            {/* アラート表示 */}
            {result.seo_analysis.alerts.length > 0 && (
              <div className="space-y-2">
                {result.seo_analysis.alerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-md ${
                      alert.type === 'warning'
                        ? 'bg-yellow-50 border border-yellow-200 text-yellow-800'
                        : alert.type === 'info'
                        ? 'bg-blue-50 border border-blue-200 text-blue-800'
                        : 'bg-green-50 border border-green-200 text-green-800'
                    }`}
                  >
                    <p className="text-sm">{alert.message}</p>
                  </div>
                ))}
              </div>
            )}

            {/* 主要指標 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">検索ボリューム</p>
                <p className="text-2xl font-bold text-gray-900">
                  {result.seo_analysis.keyword_data.search_volume.toLocaleString()}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">競合度</p>
                <p className="text-2xl font-bold text-gray-900">
                  {result.seo_analysis.keyword_data.competition_index}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {result.seo_analysis.keyword_data.competition}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">CPC</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${result.seo_analysis.keyword_data.cpc.toFixed(2)}
                </p>
              </div>
              <div className="bg-indigo-50 p-4 rounded-lg border-2 border-indigo-200">
                <p className="text-sm text-indigo-600 mb-1">総合スコア</p>
                <p className="text-3xl font-bold text-indigo-700">
                  {result.seo_analysis.scores.total_score.toFixed(1)}
                </p>
              </div>
            </div>

            {/* データ可視化 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 月次トレンド */}
              {monthlyTrendData.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">月次検索ボリューム推移</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={monthlyTrendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="volume" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* スコア比較 */}
              {scoreData.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">スコア分析</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={scoreData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip />
                      <Bar dataKey="score">
                        {scoreData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* コスト試算・ROI計算 */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">コスト試算・ROI計算</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">広告運用の場合</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">月間推定クリック数:</span>
                      <span className="font-medium">{result.seo_analysis.roi_metrics.monthly_clicks.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">月間広告費試算:</span>
                      <span className="font-medium">${result.seo_analysis.roi_metrics.monthly_ad_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">年間広告費試算:</span>
                      <span className="font-medium">${result.seo_analysis.roi_metrics.yearly_ad_cost.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">SEO運用の場合</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">月間推定獲得トラフィック:</span>
                      <span className="font-medium">{result.seo_analysis.roi_metrics.monthly_seo_traffic.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">年間推定獲得トラフィック:</span>
                      <span className="font-medium">{(result.seo_analysis.roi_metrics.monthly_seo_traffic * 12).toLocaleString()}</span>
                    </div>
                    <div className="mt-4 p-3 bg-blue-50 rounded-md">
                      <p className="text-xs text-blue-800">
                        ※ SEO運用の場合、広告費は不要ですが、コンテンツ制作・最適化に時間とコストがかかります。
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* キーワード戦略提案 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">キーワード戦略提案</h3>
              
              {/* 総合評価 */}
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-2">総合評価</h4>
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${
                          result.seo_analysis.scores.total_score >= 70
                            ? 'bg-green-500'
                            : result.seo_analysis.scores.total_score >= 50
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${result.seo_analysis.scores.total_score}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {result.seo_analysis.scores.total_score.toFixed(1)}点
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {result.seo_analysis.scores.total_score >= 70
                    ? '✅ このキーワードは記事生成に適しています。高品質なコンテンツを作成することで、効果的なSEO対策が可能です。'
                    : result.seo_analysis.scores.total_score >= 50
                    ? '⚠️ このキーワードは中程度の難易度です。競合分析と差別化戦略が重要です。'
                    : '❌ このキーワードは高競合または低ボリュームです。関連キーワードの検討を推奨します。'}
                </p>
              </div>

              {/* 推奨アクション */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">推奨アクション</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  {result.seo_analysis.scores.volume_score < 50 && (
                    <li className="flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      <span>検索ボリュームが低いため、関連キーワードを組み合わせたコンテンツ戦略を検討してください。</span>
                    </li>
                  )}
                  {result.seo_analysis.scores.competition_score < 50 && (
                    <li className="flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      <span>競合度が高いため、ロングテールキーワードや専門性の高いコンテンツで差別化を図ってください。</span>
                    </li>
                  )}
                  {result.seo_analysis.scores.cpc_score < 50 && (
                    <li className="flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      <span>CPCが高いため、広告運用よりもSEO対策に注力することでコスト効率が良くなります。</span>
                    </li>
                  )}
                  {result.seo_analysis.scores.total_score >= 70 && (
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      <span>このキーワードで高品質な記事を作成し、内部リンクと外部リンクを適切に配置してください。</span>
                    </li>
                  )}
                  {result.seo_analysis.related_keywords.length > 0 && (
                    <li className="flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      <span>関連キーワードを記事内に自然に組み込むことで、SEO効果を向上させることができます。</span>
                    </li>
                  )}
                </ul>
              </div>

              {/* 関連キーワード */}
              {result.seo_analysis.related_keywords.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">推奨関連キーワード</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.seo_analysis.related_keywords.map((kw: any, index: number) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs"
                      >
                        {kw.keyword || kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 詳細なAPI結果（折りたたみ） */}
        {result && (
          <div className="mt-6">
            <details className="border border-gray-200 rounded-lg p-4">
              <summary className="cursor-pointer text-sm font-semibold text-gray-700">
                詳細なAPI結果を表示
              </summary>
              <div className="mt-4 space-y-4">
                {Object.entries(result.results).map(([name, data]) => (
                  <div key={name} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{name}</h3>
                    {data.response_json && (
                      <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto max-h-96 overflow-y-auto">
                        {JSON.stringify(data.response_json, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}
