import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { analyzeSERP } from '../api/serp'

export default function SERPAnalysis() {
  const [keyword, setKeyword] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [languageCode, setLanguageCode] = useState('ja')

  const { mutate: analyze, data: result, isPending, error } = useMutation({
    mutationFn: () => analyzeSERP(keyword, locationCode, languageCode),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyword.trim()) {
      alert('キーワードを入力してください')
      return
    }
    analyze()
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">SERP分析</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-1">
              キーワード
            </label>
            <input
              type="text"
              id="keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="例: weather forecast"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="location_code" className="block text-sm font-medium text-gray-700 mb-1">
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
              <label htmlFor="language_code" className="block text-sm font-medium text-gray-700 mb-1">
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

          <button
            type="submit"
            disabled={isPending}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isPending ? '分析中...' : 'SERP分析を実行'}
          </button>
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
              <p className="text-sm text-gray-600">
                <strong>キーワード:</strong> {result.keyword}
              </p>
              <p className="text-sm text-gray-600">
                <strong>地域コード:</strong> {result.location_code}
              </p>
              <p className="text-sm text-gray-600">
                <strong>言語コード:</strong> {result.language_code}
              </p>
            </div>

            {/* 各APIの結果を表示 */}
            <div className="space-y-4">
              {result.results.map((data, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    リクエスト {index + 1}
                  </h3>
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
              ))}
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

