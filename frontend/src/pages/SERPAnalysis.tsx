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
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">SERP分析</h1>
        
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="例: weather forecast"
                required
              />
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
              {isPending ? '分析中...' : 'SERP分析を実行'}
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

        {/* SEO分析結果 */}
        {result?.seo_analysis && (
          <div className="mt-6 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">SEO分析結果</h2>
            
            {/* Phase 1: 見出し構造分析 */}
            {result.seo_analysis.headings_analysis && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">見出し構造パターン分析</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">平均タイトル長</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.seo_analysis.headings_analysis.avg_title_length}文字
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">推奨タイトル長（最小）</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.seo_analysis.headings_analysis.recommended_title_length.min}文字
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">推奨タイトル長（最大）</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {result.seo_analysis.headings_analysis.recommended_title_length.max}文字
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">H1パターン（頻出順）</h4>
                    <ul className="space-y-1">
                      {Object.entries(result.seo_analysis.headings_analysis.h1_patterns || {}).map(([pattern, count]) => (
                        <li key={pattern} className="text-sm text-gray-600 flex justify-between">
                          <span>{pattern}</span>
                          <span className="font-medium">{count}回</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">H2パターン（頻出順）</h4>
                    <ul className="space-y-1">
                      {Object.entries(result.seo_analysis.headings_analysis.h2_patterns || {}).map(([pattern, count]) => (
                        <li key={pattern} className="text-sm text-gray-600 flex justify-between">
                          <span>{pattern}</span>
                          <span className="font-medium">{count}回</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">H3パターン（頻出順）</h4>
                    <ul className="space-y-1">
                      {Object.entries(result.seo_analysis.headings_analysis.h3_patterns || {}).map(([pattern, count]) => (
                        <li key={pattern} className="text-sm text-gray-600 flex justify-between">
                          <span>{pattern}</span>
                          <span className="font-medium">{count}回</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Phase 1: タイトル最適化提案 */}
            {result.seo_analysis.titles_analysis && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">タイトル最適化提案</h3>
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">推奨タイトル案</h4>
                  <div className="space-y-3">
                    {result.seo_analysis.titles_analysis.title_suggestions?.map((suggestion, index) => (
                      <div key={index} className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-sm font-medium text-indigo-900">{suggestion.pattern}</span>
                          <span className="text-sm font-bold text-indigo-700">{suggestion.score}点</span>
                        </div>
                        <p className="text-sm text-indigo-800">{suggestion.example}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">感情語・行動喚起語</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(result.seo_analysis.titles_analysis.emotion_words || {}).map(([word, count]) => (
                        <span key={word} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                          {word} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">行動語</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(result.seo_analysis.titles_analysis.action_words || {}).map(([word, count]) => (
                        <span key={word} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                          {word} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Phase 1: FAQ抽出 */}
            {result.seo_analysis.faq_items && result.seo_analysis.faq_items.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">FAQ抽出（People Also Ask）</h3>
                <div className="space-y-3">
                  {result.seo_analysis.faq_items.map((faq, index) => (
                    <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start">
                        <span className="text-indigo-600 font-bold mr-2">Q{index + 1}:</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 mb-1">{faq.question}</p>
                          {faq.answer && (
                            <p className="text-sm text-gray-600">{faq.answer}</p>
                          )}
                          <span className="text-xs text-gray-500 mt-1 inline-block">
                            {faq.type === 'people_also_ask' ? 'People Also Ask' : 'Related Search'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Phase 2: キーワード最適化 */}
            {result.seo_analysis.keyword_optimization && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">キーワード最適化</h3>
                
                {/* 関連キーワード */}
                {result.seo_analysis.keyword_optimization.related_keywords?.related_keywords && (
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">推奨関連キーワード</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.seo_analysis.keyword_optimization.related_keywords.related_keywords.slice(0, 20).map((kw: any, index: number) => (
                        <span
                          key={index}
                          className={`px-3 py-1 rounded-full text-xs ${
                            kw.priority === 'high'
                              ? 'bg-indigo-100 text-indigo-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {kw.keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* キーワード密度 */}
                {result.seo_analysis.keyword_optimization.keyword_density && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">キーワード密度分析</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">平均密度</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {result.seo_analysis.keyword_optimization.keyword_density.average_density}%
                        </p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">推奨密度（最小）</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {result.seo_analysis.keyword_optimization.keyword_density.recommended_density?.min}%
                        </p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600 mb-1">推奨密度（最大）</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {result.seo_analysis.keyword_optimization.keyword_density.recommended_density?.max}%
                        </p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {result.seo_analysis.keyword_optimization.keyword_density.recommendation}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Phase 3: 競合分析 */}
            {result.seo_analysis.competitor_analysis && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">競合分析・差別化戦略</h3>
                
                {/* 差別化戦略 */}
                {result.seo_analysis.competitor_analysis.differentiation_strategy && (
                  <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h4 className="text-sm font-medium text-yellow-900 mb-2">差別化戦略</h4>
                    <p className="text-sm text-yellow-800 mb-3">
                      {result.seo_analysis.competitor_analysis.differentiation_strategy.recommendation}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-medium text-yellow-900 mb-1">差別化すべきトピック</p>
                        <div className="flex flex-wrap gap-2">
                          {result.seo_analysis.competitor_analysis.differentiation_strategy.focus_areas?.map((topic: string, index: number) => (
                            <span key={index} className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-yellow-900 mb-1">必ず含めるべきトピック</p>
                        <div className="flex flex-wrap gap-2">
                          {result.seo_analysis.competitor_analysis.differentiation_strategy.must_include?.map((topic: string, index: number) => (
                            <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* コンテンツギャップ */}
                {result.seo_analysis.competitor_analysis.content_gaps && result.seo_analysis.competitor_analysis.content_gaps.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">コンテンツギャップ（差別化のチャンス）</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.seo_analysis.competitor_analysis.content_gaps.map((gap: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                          {gap}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Phase 3: 検索意図分析 */}
            {result.seo_analysis.search_intent && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">検索意図分析</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">主要な検索意図</p>
                    <p className="text-2xl font-bold text-indigo-700">
                      {result.seo_analysis.search_intent.dominant_intent}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      信頼度: {result.seo_analysis.search_intent.confidence?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">推奨記事タイプ</p>
                    <p className="text-2xl font-bold text-indigo-700">
                      {result.seo_analysis.search_intent.recommended_article_type}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Phase 4: 自動プロンプト生成 */}
            {result.seo_analysis.prompt_generation && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">記事生成用プロンプト</h3>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {result.seo_analysis.prompt_generation.prompt}
                  </pre>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(result.seo_analysis.prompt_generation.prompt)
                    alert('プロンプトをクリップボードにコピーしました')
                  }}
                  className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  プロンプトをコピー
                </button>
              </div>
            )}

            {/* Phase 4: 構造化データ提案 */}
            {result.seo_analysis.structured_data && result.seo_analysis.structured_data.suggestions && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">構造化データ提案</h3>
                <div className="space-y-3">
                  {result.seo_analysis.structured_data.suggestions.map((suggestion: any, index: number) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${
                        suggestion.priority === 'high'
                          ? 'bg-red-50 border-red-200'
                          : 'bg-blue-50 border-blue-200'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm font-medium text-gray-900">{suggestion.type}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          suggestion.priority === 'high'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {suggestion.priority === 'high' ? '高優先度' : '中優先度'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{suggestion.reason}</p>
                      {suggestion.example && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-600 cursor-pointer">例を表示</summary>
                          <pre className="mt-2 text-xs bg-white p-2 rounded overflow-x-auto">
                            {JSON.stringify(suggestion.example, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
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
                {result.results.map((data, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      リクエスト {index + 1}
                    </h3>
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
