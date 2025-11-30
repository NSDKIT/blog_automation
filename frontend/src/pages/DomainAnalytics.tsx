import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { analyzeDomainAnalytics } from '../api/domain_analytics'

export default function DomainAnalytics() {
  const [keyword, setKeyword] = useState('')
  const [target, setTarget] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [languageCode, setLanguageCode] = useState('ja')

  const { mutate: analyze, data: result, isPending, error } = useMutation({
    mutationFn: () => analyzeDomainAnalytics(
      keyword.trim() || undefined,
      target.trim() || undefined,
      locationCode,
      languageCode
    ),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyword.trim() && !target.trim()) {
      alert('キーワードまたはターゲットサイトのいずれかを入力してください')
      return
    }
    analyze()
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Domain Analytics分析</h1>
        
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">
                キーワード（オプション）
              </label>
              <input
                type="text"
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="例: seo"
              />
              <p className="mt-1 text-xs text-gray-500">
                related_keywords, keyword_suggestions, keyword_ideasで使用されます
              </p>
            </div>
            
            <div>
              <label htmlFor="target" className="block text-sm font-medium text-gray-700 mb-2">
                ターゲットサイト（オプション）
              </label>
              <input
                type="text"
                id="target"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="例: dataforseo.com"
              />
              <p className="mt-1 text-xs text-gray-500">
                keywords_for_siteで使用されます
              </p>
            </div>

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
              {isPending ? '分析中...' : 'Domain Analytics分析を実行'}
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
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              {result.keyword && (
                <p className="text-sm text-gray-600">
                  <strong>キーワード:</strong> {result.keyword}
                </p>
              )}
              {result.target && (
                <p className="text-sm text-gray-600">
                  <strong>ターゲットサイト:</strong> {result.target}
                </p>
              )}
              <p className="text-sm text-gray-600">
                <strong>地域コード:</strong> {result.location_code}
              </p>
              <p className="text-sm text-gray-600">
                <strong>言語コード:</strong> {result.language_code}
              </p>
            </div>

            {/* 各APIの結果を表示 */}
            <div className="space-y-4">
              {result.results.map((data, index) => {
                // URLからAPI名を抽出
                const apiName = data.url.split('/').pop() || `API ${index + 1}`
                
                return (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{apiName}</h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <strong className="text-gray-700">URL:</strong>
                        <p className="text-gray-600 break-all">{data.url}</p>
                      </div>
                      <div>
                        <strong className="text-gray-700">Payload:</strong>
                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                          {data.payload}
                        </pre>
                      </div>
                      {data.headers && (
                        <div>
                          <strong className="text-gray-700">Headers:</strong>
                          <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto mt-1">
                            {JSON.stringify(data.headers, null, 2)}
                          </pre>
                        </div>
                      )}
                      {data.http_status_code !== undefined && (
                        <div>
                          <strong className="text-gray-700">HTTP Status Code:</strong>
                          <span className={`ml-2 ${
                            data.http_status_code === 200 ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            {data.http_status_code}
                          </span>
                          <p className="text-xs text-gray-500 mt-1">
                            (注: DataForSEO APIは認証成功時でも402を返す場合があります。レスポンス内のstatus_codeを確認してください)
                          </p>
                        </div>
                      )}
                      {data.error && (
                        <div>
                          <strong className="text-red-700">Error:</strong>
                          <p className="text-red-600">{data.error}</p>
                        </div>
                      )}
                      {data.response_json && (
                        <div>
                          <strong className="text-gray-700">Response (JSON):</strong>
                          <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto mt-2 max-h-96 overflow-y-auto">
                            {JSON.stringify(data.response_json, null, 2)}
                          </pre>
                        </div>
                      )}
                      {data.response_text && !data.response_json && (
                        <div>
                          <strong className="text-gray-700">Response (Text):</strong>
                          <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto mt-2 max-h-96 overflow-y-auto">
                            {data.response_text}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* 全体のJSONを表示（オプション） */}
            <div className="mt-6">
              <details className="border border-gray-200 rounded-lg p-4">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700">
                  全体のJSON結果を表示
                </summary>
                <pre className="mt-4 bg-gray-50 p-4 rounded text-xs overflow-x-auto max-h-96 overflow-y-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

