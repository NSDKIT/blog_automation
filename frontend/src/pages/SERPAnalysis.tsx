import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { analyzeSERP } from '../api/serp'
import { listIntegratedAnalyses, getIntegratedAnalysis, IntegratedAnalysisResult } from '../api/integrated_analysis_results'

export default function SERPAnalysis() {
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null)
  const [selectedKeywords, setSelectedKeywords] = useState<Set<string>>(new Set())
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [languageCode, setLanguageCode] = useState('ja')

  // 統合分析結果一覧を取得
  const { data: analyses, isLoading: analysesLoading } = useQuery({
    queryKey: ['integrated-analyses'],
    queryFn: listIntegratedAnalyses
  })

  // 選択された統合分析の詳細を取得
  const { data: selectedAnalysis, isLoading: analysisLoading } = useQuery({
    queryKey: ['integrated-analysis', selectedAnalysisId],
    queryFn: () => getIntegratedAnalysis(selectedAnalysisId!),
    enabled: !!selectedAnalysisId
  })

  // SERP分析を実行
  const { mutate: analyze, data: result, isPending, error } = useMutation({
    mutationFn: (keywords: string[]) => {
      // 複数のキーワードでSERP分析を実行（最初のキーワードを使用）
      return analyzeSERP(keywords[0], locationCode, languageCode)
    },
  })

  const handleSelectAnalysis = (analysisId: string) => {
    setSelectedAnalysisId(analysisId)
    setSelectedKeywords(new Set())
  }

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
    if (!selectedAnalysis?.related_keywords) return
    const allKeywords = selectedAnalysis.related_keywords.map((kw: any) => kw.keyword).filter(Boolean)
    setSelectedKeywords(new Set(allKeywords))
  }

  const handleDeselectAll = () => {
    setSelectedKeywords(new Set())
  }

  const handleRunSERPAnalysis = () => {
    if (selectedKeywords.size === 0) {
      alert('分析するキーワードを選択してください')
      return
    }
    analyze(Array.from(selectedKeywords))
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">SERP分析</h1>
        
        {/* ステップ1: 統合分析結果一覧 */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">ステップ1: 統合分析結果を選択</h2>
          {analysesLoading ? (
            <p className="text-gray-600">読み込み中...</p>
          ) : !analyses || analyses.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                統合分析結果がありません。まず「統合分析」タブで分析を実行してください。
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {analyses.map((analysis) => (
                <button
                  key={analysis.id}
                  onClick={() => handleSelectAnalysis(analysis.id)}
                  className={`w-full text-left p-4 border rounded-lg transition-colors ${
                    selectedAnalysisId === analysis.id
                      ? 'bg-indigo-50 border-indigo-500'
                      : 'bg-white border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">{analysis.keyword}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(analysis.created_at).toLocaleString('ja-JP')} | 
                        関連キーワード: {analysis.related_keywords?.length || 0}件
                      </p>
                    </div>
                    {selectedAnalysisId === analysis.id && (
                      <span className="text-indigo-600 font-medium">✓ 選択中</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ステップ2: 関連キーワード選択 */}
        {selectedAnalysis && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              ステップ2: 分析するキーワードを選択
            </h2>
            {analysisLoading ? (
              <p className="text-gray-600">読み込み中...</p>
            ) : (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <p className="text-sm text-gray-600">
                    選択: {selectedKeywords.size}件 / {selectedAnalysis.related_keywords?.length || 0}件
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleSelectAll}
                      className="px-3 py-1 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded text-sm"
                    >
                      全選択
                    </button>
                    <button
                      onClick={handleDeselectAll}
                      className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded text-sm"
                    >
                      全解除
                    </button>
                  </div>
                </div>
                <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {selectedAnalysis.related_keywords?.map((kw: any, index: number) => (
                      <label
                        key={index}
                        className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedKeywords.has(kw.keyword)
                            ? 'bg-indigo-50 border-indigo-500'
                            : 'bg-white border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedKeywords.has(kw.keyword)}
                          onChange={() => handleToggleKeyword(kw.keyword)}
                          className="mr-3 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900">{kw.keyword}</p>
                          <p className="text-xs text-gray-600">
                            ボリューム: {kw.search_volume?.toLocaleString() || 0} | 
                            難易度: {kw.difficulty || 'N/A'}
                          </p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ステップ3: SERP分析実行 */}
        {selectedAnalysis && selectedKeywords.size > 0 && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">ステップ3: SERP分析を実行</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  地域コード
                </label>
                <input
                  type="number"
                  value={locationCode}
                  onChange={(e) => setLocationCode(parseInt(e.target.value) || 2840)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  言語コード
                </label>
                <input
                  type="text"
                  value={languageCode}
                  onChange={(e) => setLanguageCode(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <button
              onClick={handleRunSERPAnalysis}
              disabled={isPending || selectedKeywords.size === 0}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPending ? '分析中...' : `SERP分析を実行 (${selectedKeywords.size}件のキーワード)`}
            </button>
          </div>
        )}

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
            
            {/* 見出し構造分析 */}
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
              </div>
            )}

            {/* 競合サイト分析結果 */}
            {result.seo_analysis.competitor_analysis && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">競合サイト分析結果</h3>
                
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

            {/* コンテンツ戦略提案 */}
            {result.seo_analysis.prompt_generation && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">コンテンツ戦略提案</h3>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {result.seo_analysis.prompt_generation.prompt}
                  </pre>
                </div>
                <button
                  onClick={() => {
                    if (result.seo_analysis?.prompt_generation?.prompt) {
                      navigator.clipboard.writeText(result.seo_analysis.prompt_generation.prompt)
                      alert('プロンプトをクリップボードにコピーしました')
                    }
                  }}
                  className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  プロンプトをコピー
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
