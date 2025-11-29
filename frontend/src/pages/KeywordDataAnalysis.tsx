import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import apiClient from '../api/client'

interface KeywordDataResult {
  keyword: string
  location_code: number
  results: {
    [key: string]: {
      url: string
      payload: string
      status_code?: number
      response_text?: string
      response_json?: any
      error?: string
    }
  }
}

export default function KeywordDataAnalysis() {
  const [keyword, setKeyword] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [result, setResult] = useState<KeywordDataResult | null>(null)

  const analyzeMutation = useMutation({
    mutationFn: async (data: { keyword: string; location_code: number }) => {
      const response = await apiClient.post<KeywordDataResult>(
        `/keyword-data/analyze?keyword=${encodeURIComponent(data.keyword)}&location_code=${data.location_code}`
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

        {/* 結果表示 */}
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
            </div>

            {/* 各APIの結果を表示 */}
            <div className="space-y-4">
              {Object.entries(result.results).map(([name, data]) => (
                <div key={name} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{name}</h3>
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
                    {data.status_code && (
                      <div>
                        <strong className="text-gray-700">Status Code:</strong>
                        <span className={`ml-2 ${
                          data.status_code === 200 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {data.status_code}
                        </span>
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

