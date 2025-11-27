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
      if (article?.status === 'keyword_analysis') {
        return 2000 // 2秒ごとにポーリング
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

  if (article.status === 'keyword_analysis') {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">キーワード分析中...</p>
          <p className="mt-2 text-sm text-gray-500">
            関連キーワード100個を生成し、検索ボリューム・競合度を分析しています
          </p>
        </div>
      </div>
    )
  }

  if (article.status !== 'keyword_selection') {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <p className="text-gray-600">この記事は既に処理済みです</p>
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

