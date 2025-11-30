import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { analyzeDataForSEOLabs } from '../api/dataforseo_labs'

const AVAILABLE_ENDPOINTS = [
  { value: 'related_keywords', label: 'Related Keywords', requires: ['keyword'] },
  { value: 'keywords_for_site', label: 'Keywords for Site', requires: ['target'] },
  { value: 'keyword_suggestions', label: 'Keyword Suggestions', requires: ['keyword'] },
  { value: 'keyword_ideas', label: 'Keyword Ideas', requires: ['keywords'] },
  { value: 'ranked_keywords', label: 'Ranked Keywords', requires: ['target'] },
  { value: 'serp_competitors', label: 'SERP Competitors', requires: ['keywords'] },
  { value: 'competitors_domain', label: 'Competitors Domain', requires: ['target'] },
  { value: 'domain_intersection', label: 'Domain Intersection', requires: ['target1', 'target2'] },
  { value: 'keyword_overview', label: 'Keyword Overview', requires: ['keywords'] },
  { value: 'bulk_keyword_difficulty', label: 'Bulk Keyword Difficulty', requires: ['keywords'] },
  { value: 'search_intent', label: 'Search Intent', requires: ['keywords'] },
  { value: 'top_searches', label: 'Top Searches', requires: [] },
]

export default function DataForSEOLabs() {
  const [endpoint, setEndpoint] = useState('related_keywords')
  const [keyword, setKeyword] = useState('')
  const [target, setTarget] = useState('')
  const [keywords, setKeywords] = useState('')
  const [target1, setTarget1] = useState('')
  const [target2, setTarget2] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [languageCode, setLanguageCode] = useState('ja')

  const selectedEndpoint = AVAILABLE_ENDPOINTS.find(e => e.value === endpoint)

  const { mutate: analyze, data: result, isPending, error } = useMutation({
    mutationFn: () => {
      const params: any = {
        location_code: locationCode,
        language_code: languageCode,
      }

      if (keyword) params.keyword = keyword
      if (target) params.target = target
      if (keywords) {
        params.keywords = keywords.split(',').map(k => k.trim()).filter(k => k)
      }
      if (target1) params.target1 = target1
      if (target2) params.target2 = target2

      return analyzeDataForSEOLabs(endpoint, params)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // 必須パラメータのチェック
    if (selectedEndpoint) {
      const missing = selectedEndpoint.requires.filter(req => {
        if (req === 'keyword') return !keyword.trim()
        if (req === 'target') return !target.trim()
        if (req === 'keywords') return !keywords.trim()
        if (req === 'target1') return !target1.trim()
        if (req === 'target2') return !target2.trim()
        return false
      })
      
      if (missing.length > 0) {
        alert(`以下のパラメータが必要です: ${missing.join(', ')}`)
        return
      }
    }
    
    analyze()
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">DataForSEO Labs分析</h1>
        
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="grid grid-cols-1 gap-4">
            {/* エンドポイント選択 */}
            <div>
              <label htmlFor="endpoint" className="block text-sm font-medium text-gray-700 mb-2">
                APIエンドポイント
              </label>
              <select
                id="endpoint"
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                {AVAILABLE_ENDPOINTS.map(ep => (
                  <option key={ep.value} value={ep.value}>
                    {ep.label}
                  </option>
                ))}
              </select>
              {selectedEndpoint && selectedEndpoint.requires.length > 0 && (
                <p className="mt-1 text-xs text-gray-500">
                  必須パラメータ: {selectedEndpoint.requires.join(', ')}
                </p>
              )}
            </div>

            {/* キーワード（単一） */}
            {selectedEndpoint?.requires.includes('keyword') && (
              <div>
                <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
                  キーワード *
                </label>
                <input
                  type="text"
                  id="keyword"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="例: seo"
                  required
                />
              </div>
            )}

            {/* キーワード（複数） */}
            {selectedEndpoint?.requires.includes('keywords') && (
              <div>
                <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-2">
                  キーワード（カンマ区切り） *
                </label>
                <input
                  type="text"
                  id="keywords"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="例: seo, keyword research"
                  required
                />
              </div>
            )}

            {/* ターゲットサイト（単一） */}
            {selectedEndpoint?.requires.includes('target') && (
              <div>
                <label htmlFor="target" className="block text-sm font-medium text-gray-700 mb-2">
                  ターゲットサイト *
                </label>
                <input
                  type="text"
                  id="target"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="例: dataforseo.com"
                  required
                />
              </div>
            )}

            {/* ターゲットサイト1 */}
            {selectedEndpoint?.requires.includes('target1') && (
              <div>
                <label htmlFor="target1" className="block text-sm font-medium text-gray-700 mb-2">
                  ターゲットサイト1 *
                </label>
                <input
                  type="text"
                  id="target1"
                  value={target1}
                  onChange={(e) => setTarget1(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="例: dataforseo.com"
                  required
                />
              </div>
            )}

            {/* ターゲットサイト2 */}
            {selectedEndpoint?.requires.includes('target2') && (
              <div>
                <label htmlFor="target2" className="block text-sm font-medium text-gray-700 mb-2">
                  ターゲットサイト2 *
                </label>
                <input
                  type="text"
                  id="target2"
                  value={target2}
                  onChange={(e) => setTarget2(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="例: seopanel.org"
                  required
                />
              </div>
            )}

            {/* 地域コードと言語コード */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="location_code" className="block text-sm font-medium text-gray-700 mb-2">
                  地域コード
                </label>
                <input
                  type="number"
                  id="location_code"
                  value={locationCode}
                  onChange={(e) => setLocationCode(parseInt(e.target.value) || 2840)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="2840 (日本)"
                />
              </div>
              <div>
                <label htmlFor="language_code" className="block text-sm font-medium text-gray-700 mb-2">
                  言語コード
                </label>
                <input
                  type="text"
                  id="language_code"
                  value={languageCode}
                  onChange={(e) => setLanguageCode(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="ja"
                />
              </div>
            </div>
          </div>
          <div className="mt-4">
            <button
              type="submit"
              disabled={isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPending ? '分析中...' : 'DataForSEO Labs分析を実行'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">
              エラーが発生しました: {error instanceof Error ? error.message : '不明なエラー'}
            </p>
          </div>
        )}

        {result && (
          <div className="mt-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">分析結果</h2>
            
            <div className="space-y-4">
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">APIレスポンス</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong className="text-gray-700">URL:</strong>
                    <p className="text-gray-600 break-all">{result.url}</p>
                  </div>
                  <div>
                    <strong className="text-gray-700">Payload:</strong>
                    <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                      {result.payload}
                    </pre>
                  </div>
                  {result.headers && (
                    <div>
                      <strong className="text-gray-700">Headers:</strong>
                      <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto mt-1">
                        {JSON.stringify(result.headers, null, 2)}
                      </pre>
                    </div>
                  )}
                  {result.http_status_code !== undefined && (
                    <div>
                      <strong className="text-gray-700">HTTP Status Code:</strong>
                      <span className={`ml-2 ${
                        result.http_status_code === 200 ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        {result.http_status_code}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        (注: DataForSEO APIは認証成功時でも402を返す場合があります。レスポンス内のstatus_codeを確認してください)
                      </p>
                    </div>
                  )}
                  {result.error && (
                    <div>
                      <strong className="text-red-700">Error:</strong>
                      <p className="text-red-600">{result.error}</p>
                    </div>
                  )}
                  {result.response_json && (
                    <div>
                      <strong className="text-gray-700">Response (JSON):</strong>
                      <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto mt-2 max-h-96 overflow-y-auto">
                        {JSON.stringify(result.response_json, null, 2)}
                      </pre>
                    </div>
                  )}
                  {result.response_text && !result.response_json && (
                    <div>
                      <strong className="text-gray-700">Response (Text):</strong>
                      <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto mt-2 max-h-96 overflow-y-auto">
                        {result.response_text}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

