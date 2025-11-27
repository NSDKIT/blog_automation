import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { articlesApi } from '../api/articles'
import { useMemo, useState, useEffect, useRef } from 'react'
import DOMPurify from 'dompurify'

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedContent, setEditedContent] = useState('')
  const hasRedirected = useRef(false)

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', id],
    queryFn: () => articlesApi.getArticle(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const article = query.state.data
      // キーワード分析中またはキーワード選択待ちの場合はポーリング
      if (article?.status === 'keyword_analysis' || article?.status === 'keyword_selection') {
        return 2000 // 2秒ごとにポーリング
      }
      return false
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: { title?: string; content?: string }) =>
      articlesApi.updateArticle(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', id] })
      setIsEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => articlesApi.deleteArticle(id!),
    onSuccess: () => {
      navigate('/')
    },
  })

  const publishMutation = useMutation({
    mutationFn: () => articlesApi.publishArticle(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', id] })
      alert('Shopifyに投稿しました')
    },
  })

  const publishWordPressMutation = useMutation({
    mutationFn: () => articlesApi.publishToWordPress(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['article', id] })
      alert('WordPressに投稿しました')
    },
    onError: (error: any) => {
      alert(`WordPress投稿エラー: ${error.response?.data?.detail || error.message}`)
    },
  })


  const sanitizedContent = useMemo(() => {
    if (!article?.content) {
      return ''
    }
    return DOMPurify.sanitize(article.content)
  }, [article?.content])

  if (isLoading) {
    return <div className="text-center py-12">読み込み中...</div>
  }

  // キーワード分析が完了したら自動でキーワード選択画面にリダイレクト
  useEffect(() => {
    if (article?.status === 'keyword_selection' && !location.pathname.includes('/keywords') && !hasRedirected.current) {
      hasRedirected.current = true
      navigate(`/articles/${id}/keywords`)
    }
    // ステータスが変わったらリセット
    if (article?.status !== 'keyword_selection') {
      hasRedirected.current = false
    }
  }, [article?.status, id, navigate, location.pathname])

  if (!article) {
    return <div className="text-center py-12">記事が見つかりません</div>
  }

  // キーワード選択が必要な場合
  if (article.status === 'keyword_selection') {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">キーワード選択が必要です</h1>
          <p className="text-gray-600 mb-6">
            関連キーワード100個の分析が完了しました。<br />
            記事に使用するキーワードを選択してください。
          </p>
          <button
            onClick={() => navigate(`/articles/${id}/keywords`)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium"
          >
            キーワードを選択する
          </button>
        </div>
      </div>
    )
  }

  // キーワード分析中の場合
  if (article.status === 'keyword_analysis') {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <h1 className="text-xl font-bold text-gray-900 mt-4 mb-2">キーワード分析中</h1>
          <p className="text-gray-600">
            関連キーワード100個を生成し、検索ボリューム・競合度を分析しています...
          </p>
          <p className="text-sm text-gray-500 mt-2">
            この処理には約30-60秒かかります
          </p>
          <p className="text-xs text-gray-400 mt-4">
            分析が完了すると自動でキーワード選択画面に移動します
          </p>
        </div>
      </div>
    )
  }

  const handleSave = () => {
    updateMutation.mutate({
      title: editedTitle || article.title || undefined,
      content: editedContent || article.content || undefined,
    })
  }

  if (isEditing) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              タイトル
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={editedTitle || article.title || ''}
              onChange={(e) => setEditedTitle(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              内容
            </label>
            <textarea
              rows={20}
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={editedContent || article.content || ''}
              onChange={(e) => setEditedContent(e.target.value)}
            />
          </div>
          <div className="flex justify-end space-x-4">
            <button
              onClick={() => setIsEditing(false)}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
            >
              キャンセル
            </button>
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              保存
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {article.title || article.keyword}
            </h1>
            <div className="text-sm text-gray-500">
              <p>キーワード: {article.keyword}</p>
              <p>ターゲット: {article.target} | 種類: {article.article_type}</p>
              <p>ステータス: {article.status}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                setEditedTitle(article.title || '')
                setEditedContent(article.content || '')
                setIsEditing(true)
              }}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              編集
            </button>
            {article.status === 'completed' && (
              <>
                <button
                  onClick={() => publishMutation.mutate()}
                  disabled={publishMutation.isPending}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {publishMutation.isPending ? '投稿中...' : 'Shopifyに投稿'}
                </button>
                <button
                  onClick={() => publishWordPressMutation.mutate()}
                  disabled={publishWordPressMutation.isPending}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {publishWordPressMutation.isPending ? '投稿中...' : 'WordPressに投稿'}
                </button>
              </>
            )}
            <button
              onClick={() => {
                if (confirm('本当に削除しますか？')) {
                  deleteMutation.mutate()
                }
              }}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              削除
            </button>
          </div>
        </div>

        {article.status === 'failed' && (
          <div className="mb-6 rounded-md border border-red-200 bg-red-50 p-4 text-red-700">
            <p className="font-semibold">記事生成に失敗しました</p>
            <p className="mt-1 text-sm whitespace-pre-wrap break-words">
              {article.error_message ?? '詳細は管理者にお問い合わせください。'}
            </p>
          </div>
        )}

        {/* SEO分析結果 */}
        {(article.meta_title || article.serp_data || article.keyword_difficulty) && (
          <div className="mb-6 border-t pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">SEO分析結果</h2>
            
            {/* メタタグ */}
            {(article.meta_title || article.meta_description) && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">メタタグ</h3>
                {article.meta_title && (
                  <div className="mb-2">
                    <p className="text-xs text-gray-500">メタタイトル</p>
                    <p className="text-sm text-gray-900">{article.meta_title}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {article.meta_title.length}文字 {article.meta_title.length > 60 ? '(長すぎます)' : '(適切)'}
                    </p>
                  </div>
                )}
                {article.meta_description && (
                  <div>
                    <p className="text-xs text-gray-500">メタディスクリプション</p>
                    <p className="text-sm text-gray-900">{article.meta_description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {article.meta_description.length}文字 {article.meta_description.length > 160 ? '(長すぎます)' : '(適切)'}
                    </p>
                  </div>
                )}
              </div>
            )}
            
            {/* キーワード難易度 */}
            {article.keyword_difficulty && (
              <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">キーワード情報</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {article.keyword_difficulty.search_volume && (
                    <div>
                      <p className="text-xs text-gray-500">検索ボリューム</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.keyword_difficulty.search_volume.toLocaleString()}
                      </p>
                    </div>
                  )}
                  {article.keyword_difficulty.competition_index !== undefined && (
                    <div>
                      <p className="text-xs text-gray-500">競合度</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.keyword_difficulty.competition_index}/100
                      </p>
                    </div>
                  )}
                  {article.keyword_difficulty.cpc && (
                    <div>
                      <p className="text-xs text-gray-500">CPC</p>
                      <p className="text-lg font-semibold text-gray-900">
                        ¥{article.keyword_difficulty.cpc.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* SERP分析結果 */}
            {article.serp_common_patterns && (
              <div className="mb-4 p-4 bg-green-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">SERP分析結果</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {article.serp_common_patterns.definition > 0 && (
                    <div>
                      <p className="text-xs text-gray-500">定義型</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.serp_common_patterns.definition}件
                      </p>
                    </div>
                  )}
                  {article.serp_common_patterns.how_to > 0 && (
                    <div>
                      <p className="text-xs text-gray-500">方法型</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.serp_common_patterns.how_to}件
                      </p>
                    </div>
                  )}
                  {article.serp_common_patterns.recommendation > 0 && (
                    <div>
                      <p className="text-xs text-gray-500">おすすめ型</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.serp_common_patterns.recommendation}件
                      </p>
                    </div>
                  )}
                  {article.serp_common_patterns.comparison > 0 && (
                    <div>
                      <p className="text-xs text-gray-500">比較型</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {article.serp_common_patterns.comparison}件
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* FAQ項目 */}
            {article.serp_faq_items && article.serp_faq_items.length > 0 && (
              <div className="mb-4 p-4 bg-yellow-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">FAQ項目（People Also Ask）</h3>
                <ul className="list-disc list-inside space-y-1">
                  {article.serp_faq_items.slice(0, 5).map((faq, index) => (
                    <li key={index} className="text-sm text-gray-700">{faq}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* サブトピック */}
            {article.subtopics && article.subtopics.length > 0 && (
              <div className="mb-4 p-4 bg-purple-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">推奨サブトピック</h3>
                <div className="flex flex-wrap gap-2">
                  {article.subtopics.map((topic, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* 最適なキーワード */}
            {article.best_keywords && article.best_keywords.length > 0 && (
              <div className="mb-4 p-4 bg-indigo-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  最適なキーワード（スコアリング済み）
                </h3>
                <div className="space-y-2">
                  {article.best_keywords.slice(0, 10).map((kw: any, index: number) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-white rounded border"
                    >
                      <div className="flex-1">
                        <span className="font-medium text-gray-900">{kw.keyword}</span>
                        <div className="text-xs text-gray-500 mt-1">
                          検索ボリューム: {kw.search_volume?.toLocaleString() || 0} | 
                          競合度: {kw.competition_index || 0}/100 | 
                          CPC: ¥{kw.cpc?.toFixed(2) || '0.00'}
                        </div>
                      </div>
                      <div className="ml-4 text-right">
                        <div className="text-lg font-bold text-indigo-600">
                          {kw.total_score?.toFixed(1) || '0.0'}
                        </div>
                        <div className="text-xs text-gray-500">スコア</div>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  ※ スコア = (検索ボリュームスコア × 0.6) + (競合度スコア × 0.4)
                </p>
              </div>
            )}
          </div>
        )}

        <div className="prose max-w-none">
          {article.content ? (
            <div
              className="whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: sanitizedContent }}
            />
          ) : (
            <div className="text-center py-12 text-gray-500">
              {article.status === 'processing' ? '記事を生成中です...' : '記事内容がありません'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
