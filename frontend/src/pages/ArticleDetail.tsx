import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { articlesApi } from '../api/articles'
import { useState } from 'react'

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedContent, setEditedContent] = useState('')

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', id],
    queryFn: () => articlesApi.getArticle(id!),
    enabled: !!id,
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

  if (isLoading) {
    return <div className="text-center py-12">読み込み中...</div>
  }

  if (!article) {
    return <div className="text-center py-12">記事が見つかりません</div>
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
              <button
                onClick={() => publishMutation.mutate()}
                disabled={publishMutation.isPending}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {publishMutation.isPending ? '投稿中...' : 'Shopifyに投稿'}
              </button>
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

        <div className="prose max-w-none">
          {article.content ? (
            <div
              className="whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: article.content }}
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

