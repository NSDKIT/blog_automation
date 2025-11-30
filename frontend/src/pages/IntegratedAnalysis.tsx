import { useState, useMemo } from 'react'
import { useMutation } from '@tanstack/react-query'
import apiClient from '../api/client'
import { analyzeSERP } from '../api/serp'
import { analyzeDomainAnalytics } from '../api/domain_analytics'
import { analyzeDataForSEOLabs } from '../api/dataforseo_labs'

type FilterType = 'all' | 'immediate' | 'medium' | 'long'
type SortType = 'priority' | 'volume' | 'difficulty_asc' | 'difficulty_desc' | 'cpc' | 'rank'

export default function IntegratedAnalysis() {
  const [keyword, setKeyword] = useState('')
  const [locationCode, setLocationCode] = useState(2840) // 日本
  const [languageCode, setLanguageCode] = useState('ja')
  const [selectedKeywords, setSelectedKeywords] = useState<Set<string>>(new Set())
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [sortType, setSortType] = useState<SortType>('priority')
  const [volumeFilter, setVolumeFilter] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 20

  const mutation = useMutation({
    mutationFn: async () => {
      // 各タブの既存エンドポイントを順次呼び出し（サーバー負荷を軽減）
      // リトライロジック付きのヘルパー関数
      const retryRequest = async <T,>(
        requestFn: () => Promise<T>,
        maxRetries: number = 3,
        delay: number = 2000
      ): Promise<T> => {
        for (let i = 0; i < maxRetries; i++) {
          try {
            return await requestFn()
          } catch (error: any) {
            const isLastAttempt = i === maxRetries - 1
            const isRetryable = error?.response?.status === 503 || error?.response?.status === 429 || error?.code === 'ECONNABORTED'
            
            if (isLastAttempt || !isRetryable) {
              throw error
            }
            
            // リトライ前に待機
            await new Promise(resolve => setTimeout(resolve, delay * (i + 1)))
          }
        }
        throw new Error('Max retries exceeded')
      }
      
      // 1. Keyword Data Analysis
      const keywordDataResult = await retryRequest(async () => {
        const response = await apiClient.post(
          `/keyword-data/analyze?keyword=${encodeURIComponent(keyword)}&location_code=${locationCode}`,
          {},
          { timeout: 120000 }
        )
        return response.data
      })
      
      // 少し待機してから次のリクエスト
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 2. Domain Analytics
      const domainAnalyticsResult = await retryRequest(async () => {
        return await analyzeDomainAnalytics(keyword, undefined, locationCode, languageCode)
      })
      
      // 少し待機してから次のリクエスト
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 3. DataForSEO Labs (related_keywords)
      const dataforseoLabsResult = await retryRequest(async () => {
        return await analyzeDataForSEOLabs('related_keywords', {
          keyword,
          location_code: locationCode,
          language_code: languageCode
        })
      })
      
      // SERP Analysisはオプション（エラーが発生しても続行）
      let serpResult = null
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        serpResult = await analyzeSERP(keyword, locationCode, languageCode)
      } catch (error) {
        console.warn('SERP Analysis failed, continuing without it:', error)
      }
      
      // 結果を統合分析の形式に変換
      return transformToIntegratedResult(keywordDataResult, serpResult, domainAnalyticsResult, dataforseoLabsResult)
    },
    onSuccess: () => {
      setSelectedKeywords(new Set())
      setCurrentPage(1)
    }
  })
  
  // 優先度スコアを計算
  const calculatePriorityScore = (item: any) => {
    const volume = item.search_volume || 0
    const difficulty = item.keyword_difficulty || 50
    const cpc = item.cpc || 0
    
    // 検索ボリュームスコア（0-40点）
    const volumeScore = Math.min(40, Math.log10(volume + 1) * 10)
    
    // 難易度スコア（0-30点、難易度が低いほど高得点）
    const difficultyScore = (100 - difficulty) * 0.3
    
    // CPCスコア（0-30点）
    const cpcScore = Math.min(30, cpc * 2)
    
    return volumeScore + difficultyScore + cpcScore
  }
  
  // 推奨順位を推定
  const estimateRecommendedRank = (difficulty: number) => {
    if (difficulty < 30) return 1
    if (difficulty < 50) return 5
    if (difficulty < 70) return 10
    return 20
  }
  
  // 各APIの結果を統合分析の形式に変換する関数
  const transformToIntegratedResult = (keywordData: any, _serp: any, domainAnalytics: any, dataforseoLabs: any) => {
    // メインキーワードデータを取得
    const mainKeywordData = keywordData?.seo_analysis?.keyword_data
    const mainKeyword = mainKeywordData ? {
      keyword: mainKeywordData.keyword,
      search_volume: mainKeywordData.search_volume || 0,
      cpc: mainKeywordData.cpc || 0,
      competition: mainKeywordData.competition || 'low',
      competition_index: mainKeywordData.competition_index || 0,
      difficulty: 50, // デフォルト値
      difficulty_level: 'medium'
    } : null
    
    // 関連キーワードを取得（Domain AnalyticsとDataForSEO Labsから）
    const relatedKeywords: any[] = []
    
    // Domain Analyticsから関連キーワードを抽出
    if (domainAnalytics?.results) {
      for (const result of domainAnalytics.results) {
        if (result.response_json?.tasks?.[0]?.result?.[0]?.items) {
          for (const item of result.response_json.tasks[0].result[0].items) {
            const difficulty = item.keyword_difficulty || 50
            relatedKeywords.push({
              keyword: item.keyword || '',
              search_volume: item.search_volume || 0,
              cpc: item.cpc || 0,
              competition: item.competition || 'low',
              competition_index: item.competition_index || 0,
              difficulty: difficulty,
              difficulty_level: difficulty < 30 ? '即攻略' : difficulty < 70 ? '中期目標' : '長期目標',
              priority_score: calculatePriorityScore(item),
              recommended_rank: estimateRecommendedRank(difficulty)
            })
          }
        }
      }
    }
    
    // DataForSEO Labsから関連キーワードを抽出
    if (dataforseoLabs?.response_json?.tasks?.[0]?.result?.[0]?.items) {
      for (const item of dataforseoLabs.response_json.tasks[0].result[0].items) {
        // 重複チェック
        if (!relatedKeywords.find(rk => rk.keyword === item.keyword)) {
          const difficulty = item.keyword_difficulty || 50
          relatedKeywords.push({
            keyword: item.keyword || '',
            search_volume: item.search_volume || 0,
            cpc: item.cpc || 0,
            competition: item.competition || 'low',
            competition_index: item.competition_index || 0,
            difficulty: difficulty,
            difficulty_level: difficulty < 30 ? '即攻略' : difficulty < 70 ? '中期目標' : '長期目標',
            priority_score: calculatePriorityScore(item),
            recommended_rank: estimateRecommendedRank(difficulty)
          })
        }
      }
    }
    
    // 優先度スコアでソート
    relatedKeywords.sort((a, b) => b.priority_score - a.priority_score)
    
    // サマリーステータスを計算
    const immediate = relatedKeywords.filter(kw => kw.difficulty_level === '即攻略')
    const medium = relatedKeywords.filter(kw => kw.difficulty_level === '中期目標')
    const long = relatedKeywords.filter(kw => kw.difficulty_level === '長期目標')
    
    const summaryStats = {
      immediate_attack: {
        count: immediate.length,
        total_volume: immediate.reduce((sum, kw) => sum + kw.search_volume, 0)
      },
      medium_term: {
        count: medium.length,
        total_volume: medium.reduce((sum, kw) => sum + kw.search_volume, 0)
      },
      long_term: {
        count: long.length,
        total_volume: long.reduce((sum, kw) => sum + kw.search_volume, 0)
      }
    }
    
    // 推奨戦略
    const recommendedStrategy = {
      phase1: {
        keywords: immediate.slice(0, 10),
        estimated_traffic: immediate.slice(0, 10).reduce((sum, kw) => sum + (kw.search_volume * 0.1), 0),
        period: '1-3ヶ月'
      }
    }
    
    return {
      main_keyword: mainKeyword,
      related_keywords: relatedKeywords,
      summary_stats: summaryStats,
      recommended_strategy: recommendedStrategy,
      total_count: relatedKeywords.length
    }
  }

  // フィルター適用
  const filteredKeywords = useMemo(() => {
    if (!mutation.data?.related_keywords) return []
    
    let filtered = [...mutation.data.related_keywords]
    
    // 判定フィルター
    if (filterType === 'immediate') {
      filtered = filtered.filter(kw => kw.difficulty_level === '即攻略')
    } else if (filterType === 'medium') {
      filtered = filtered.filter(kw => kw.difficulty_level === '中期目標')
    } else if (filterType === 'long') {
      filtered = filtered.filter(kw => kw.difficulty_level === '長期目標')
    }
    
    // ボリュームフィルター
    if (volumeFilter === '100k') {
      filtered = filtered.filter(kw => kw.search_volume >= 100000)
    } else if (volumeFilter === '500k') {
      filtered = filtered.filter(kw => kw.search_volume >= 500000)
    } else if (volumeFilter === '1m') {
      filtered = filtered.filter(kw => kw.search_volume >= 1000000)
    }
    
    // ソート
    filtered.sort((a, b) => {
      switch (sortType) {
        case 'priority':
          return b.priority_score - a.priority_score
        case 'volume':
          return b.search_volume - a.search_volume
        case 'difficulty_asc':
          return a.difficulty - b.difficulty
        case 'difficulty_desc':
          return b.difficulty - a.difficulty
        case 'cpc':
          return b.cpc - a.cpc
        case 'rank':
          return a.recommended_rank - b.recommended_rank
        default:
          return 0
      }
    })
    
    return filtered
  }, [mutation.data, filterType, volumeFilter, sortType])

  // ページネーション
  const paginatedKeywords = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return filteredKeywords.slice(startIndex, startIndex + itemsPerPage)
  }, [filteredKeywords, currentPage])

  const totalPages = Math.ceil(filteredKeywords.length / itemsPerPage)

  const handleSelectKeyword = (kw: string) => {
    const newSelected = new Set(selectedKeywords)
    if (newSelected.has(kw)) {
      newSelected.delete(kw)
    } else {
      newSelected.add(kw)
    }
    setSelectedKeywords(newSelected)
  }

  const handleSelectAll = (type?: FilterType) => {
    const keywordsToSelect = type
      ? filteredKeywords.filter(kw => {
          if (type === 'immediate') return kw.difficulty_level === '即攻略'
          if (type === 'medium') return kw.difficulty_level === '中期目標'
          if (type === 'long') return kw.difficulty_level === '長期目標'
          return true
        })
      : filteredKeywords
    
    const newSelected = new Set(selectedKeywords)
    keywordsToSelect.forEach(kw => newSelected.add(kw.keyword))
    setSelectedKeywords(newSelected)
  }

  const handleDeselectAll = () => {
    setSelectedKeywords(new Set())
  }

  const handleSelectTop10 = () => {
    const top10 = filteredKeywords.slice(0, 10)
    const newSelected = new Set(selectedKeywords)
    top10.forEach(kw => newSelected.add(kw.keyword))
    setSelectedKeywords(newSelected)
  }

  const getDifficultyEmoji = (level: string) => {
    if (level === '即攻略') return '🟢'
    if (level === '中期目標') return '🟡'
    return '🔴'
  }

  const exportToCSV = () => {
    if (!mutation.data) return
    
    const headers = ['優先順位', '判定', 'キーワード', '検索ボリューム', 'CPC', '競合度', '難易度', '推奨順位', '優先度スコア']
    const rows = filteredKeywords.map((kw, index) => [
      index + 1,
      kw.difficulty_level,
      kw.keyword,
      kw.search_volume,
      kw.cpc,
      kw.competition,
      kw.difficulty,
      kw.recommended_rank,
      kw.priority_score
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')
    
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `keyword_analysis_${keyword}_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ja-JP').format(num)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">SEOキーワード分析ツール</h1>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              調査したいキーワードを入力:
            </label>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="weather forecast"
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                地域:
              </label>
              <select
                value={locationCode}
                onChange={(e) => setLocationCode(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value={2840}>Japan</option>
                <option value={2826}>United States</option>
                <option value={2825}>United Kingdom</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                言語:
              </label>
              <select
                value={languageCode}
                onChange={(e) => setLanguageCode(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="ja">日本語</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
          
          <button
            onClick={() => mutation.mutate()}
            disabled={!keyword || mutation.isPending}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-md disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {mutation.isPending ? '分析中...' : '包括分析を開始'}
          </button>
          
          {!mutation.isPending && (
            <p className="text-sm text-gray-500 text-center">⏱ 推定処理時間: 約30-60秒</p>
          )}
        </div>
      </div>

      {mutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 font-semibold mb-2">
            エラーが発生しました
          </p>
          <p className="text-red-700 text-sm">
            {mutation.error instanceof Error 
              ? mutation.error.message 
              : 'Unknown error'}
          </p>
          {mutation.error && typeof mutation.error === 'object' && 'response' in mutation.error && (
            <div className="mt-2 text-xs text-red-600">
              <p>詳細: {JSON.stringify(
                (mutation.error as any).response?.data || mutation.error, 
                null, 
                2
              )}</p>
            </div>
          )}
        </div>
      )}

      {mutation.data && (
        <div className="space-y-6">
          {/* メインキーワード分析 */}
          {mutation.data.main_keyword && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 メインキーワード分析:</h2>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="space-y-2">
                  <p><span className="font-medium">キーワード:</span> {mutation.data.main_keyword.keyword}</p>
                  <p>
                    <span className="font-medium">検索ボリューム:</span> {formatNumber(mutation.data.main_keyword.search_volume)}/月 | 
                    <span className="font-medium"> CPC:</span> ${mutation.data.main_keyword.cpc} | 
                    <span className="font-medium"> 競合:</span> {mutation.data.main_keyword.competition} | 
                    <span className="font-medium"> 難易度:</span> {mutation.data.main_keyword.difficulty}
                  </p>
                  <p>
                    <span className="font-medium">判定:</span> {getDifficultyEmoji(mutation.data.main_keyword.difficulty_level)} {mutation.data.main_keyword.difficulty_level}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* 関連キーワード分析 */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              📋 関連キーワード分析（{mutation.data.total_count}件取得）
            </h2>
            
            {/* フィルター・ソート */}
            <div className="mb-4 space-y-2">
              <div className="flex flex-wrap gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">判定:</label>
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value as FilterType)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="all">すべて</option>
                    <option value="immediate">🟢即攻略</option>
                    <option value="medium">🟡中期</option>
                    <option value="long">🔴長期</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ボリューム:</label>
                  <select
                    value={volumeFilter}
                    onChange={(e) => setVolumeFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="all">すべて</option>
                    <option value="100k">10万以上</option>
                    <option value="500k">50万以上</option>
                    <option value="1m">100万以上</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">並び替え:</label>
                  <select
                    value={sortType}
                    onChange={(e) => setSortType(e.target.value as SortType)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="priority">優先度スコア順</option>
                    <option value="volume">検索ボリューム順</option>
                    <option value="difficulty_asc">難易度順（昇順）</option>
                    <option value="difficulty_desc">難易度順（降順）</option>
                    <option value="cpc">CPC順</option>
                    <option value="rank">推奨順位順</option>
                  </select>
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                表示: {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, filteredKeywords.length)} / {filteredKeywords.length}件
              </div>
            </div>
            
            {/* キーワードテーブル */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">選択</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">優先</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">判定</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">キーワード</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ボリューム</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPC</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">競合</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">難易度</th>
                    <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">推奨順位</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedKeywords.map((kw, index) => (
                    <tr key={kw.keyword} className={selectedKeywords.has(kw.keyword) ? 'bg-blue-50' : ''}>
                      <td className="px-2 py-4 whitespace-nowrap">
                        <input
                          type="checkbox"
                          checked={selectedKeywords.has(kw.keyword)}
                          onChange={() => handleSelectKeyword(kw.keyword)}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {(currentPage - 1) * itemsPerPage + index + 1}
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm">
                        {getDifficultyEmoji(kw.difficulty_level)}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-900">{kw.keyword}</td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatNumber(kw.search_volume)}
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${kw.cpc}
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-500">
                        {kw.competition}
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-500">
                        {kw.difficulty}
                      </td>
                      <td className="px-2 py-4 whitespace-nowrap text-sm text-gray-500">
                        {kw.recommended_rank}位
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* ページネーション */}
            {totalPages > 1 && (
              <div className="mt-4 flex justify-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
                >
                  前へ
                </button>
                <span className="px-4 py-2 text-sm text-gray-700">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
                >
                  次へ
                </button>
              </div>
            )}
          </div>

          {/* サマリー統計 */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📈 サマリー統計:</h2>
            <div className="space-y-2">
              <p>
                • 🟢 即攻略可能（LOW競合）: {mutation.data.summary_stats.immediate_attack.count}件 - 
                合計ボリューム: {formatNumber(mutation.data.summary_stats.immediate_attack.total_volume)}
              </p>
              <p>
                • 🟡 中期目標（MED競合）: {mutation.data.summary_stats.medium_term.count}件 - 
                合計ボリューム: {formatNumber(mutation.data.summary_stats.medium_term.total_volume)}
              </p>
              <p>
                • 🔴 長期目標（HIGH競合）: {mutation.data.summary_stats.long_term.count}件 - 
                合計ボリューム: {formatNumber(mutation.data.summary_stats.long_term.total_volume)}
              </p>
            </div>
          </div>

          {/* AI推奨戦略 */}
          {mutation.data.recommended_strategy.phase1 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">💡 AI推奨戦略:</h2>
              <p className="mb-2">
                Phase 1（{mutation.data.recommended_strategy.phase1.period}）: 🟢マークの上位10件から着手
              </p>
              <p>
                → 想定獲得トラフィック: 月間 約{formatNumber(Math.round(mutation.data.recommended_strategy.phase1.estimated_traffic))}訪問者（CTR 3%想定）
              </p>
            </div>
          )}

          {/* キーワード選択アクション */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm font-medium text-gray-700">
                ☑ 選択: {selectedKeywords.size}件
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleSelectTop10}
                  className="px-4 py-2 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-md text-sm font-medium"
                >
                  上位10件を自動選択
                </button>
                <button
                  onClick={() => handleSelectAll('immediate')}
                  className="px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-md text-sm font-medium"
                >
                  🟢マーク全選択
                </button>
                <button
                  onClick={() => handleSelectAll()}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm font-medium"
                >
                  カスタム選択
                </button>
                <button
                  onClick={handleDeselectAll}
                  className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-md text-sm font-medium"
                >
                  全解除
                </button>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={exportToCSV}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md text-sm font-medium"
              >
                📄 レポートダウンロード（CSV）
              </button>
              <button
                onClick={() => {
                  setKeyword('')
                  setSelectedKeywords(new Set())
                  mutation.reset()
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md text-sm font-medium"
              >
                新規調査
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

