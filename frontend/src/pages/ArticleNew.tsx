import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { articlesApi, ArticleCreate } from '../api/articles'
import { optionsApi } from '../api/options'

export default function ArticleNew() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<ArticleCreate>({
    keyword: '',
    target: '',
    article_type: '',
    used_type1: '',
    used_type2: '',
    used_type3: '',
    prompt: '',
    important_keyword1: '',
    important_keyword2: '',
    important_keyword3: '',
  })

  // 登録された選択肢を取得
  const { data: targetOptions } = useQuery({
    queryKey: ['options', 'target'],
    queryFn: () => optionsApi.getOptions('target'),
  })

  const { data: articleTypeOptions } = useQuery({
    queryKey: ['options', 'article_type'],
    queryFn: () => optionsApi.getOptions('article_type'),
  })

  const { data: usedTypeOptions } = useQuery({
    queryKey: ['options', 'used_type'],
    queryFn: () => optionsApi.getOptions('used_type'),
  })

  const { data: importantKeywordOptions } = useQuery({
    queryKey: ['options', 'important_keyword'],
    queryFn: () => optionsApi.getOptions('important_keyword'),
  })

  const createMutation = useMutation({
    mutationFn: articlesApi.createArticle,
    onSuccess: (data) => {
      navigate(`/articles/${data.id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">新規記事生成</h1>

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              キーワード <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={formData.keyword}
              onChange={(e) => setFormData({ ...formData, keyword: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              ターゲット層 <span className="text-red-500">*</span>
            </label>
            <select
              required
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={formData.target}
              onChange={(e) => setFormData({ ...formData, target: e.target.value })}
            >
              <option value="">選択してください</option>
              {targetOptions?.map((option) => (
                <option key={option.id} value={option.value}>
                  {option.value}
                </option>
              ))}
            </select>
            {(!targetOptions || targetOptions.length === 0) && (
              <p className="mt-1 text-xs text-gray-500">
                設定画面で選択肢を登録してください
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              記事の種類 <span className="text-red-500">*</span>
            </label>
            <select
              required
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={formData.article_type}
              onChange={(e) => setFormData({ ...formData, article_type: e.target.value })}
            >
              <option value="">選択してください</option>
              {articleTypeOptions?.map((option) => (
                <option key={option.id} value={option.value}>
                  {option.value}
                </option>
              ))}
            </select>
            {(!articleTypeOptions || articleTypeOptions.length === 0) && (
              <p className="mt-1 text-xs text-gray-500">
                設定画面で選択肢を登録してください
              </p>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">使用シーン1</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.used_type1}
                onChange={(e) => setFormData({ ...formData, used_type1: e.target.value })}
              >
                <option value="">選択してください</option>
                {usedTypeOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">使用シーン2</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.used_type2}
                onChange={(e) => setFormData({ ...formData, used_type2: e.target.value })}
              >
                <option value="">選択してください</option>
                {usedTypeOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">使用シーン3</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.used_type3}
                onChange={(e) => setFormData({ ...formData, used_type3: e.target.value })}
              >
                <option value="">選択してください</option>
                {usedTypeOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {(!usedTypeOptions || usedTypeOptions.length === 0) && (
            <p className="text-xs text-gray-500">
              設定画面で選択肢を登録してください
            </p>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">システムプロンプト</label>
            <textarea
              rows={3}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">重要視したいキーワード1</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.important_keyword1}
                onChange={(e) => setFormData({ ...formData, important_keyword1: e.target.value })}
              >
                <option value="">選択してください</option>
                {importantKeywordOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">重要視したいキーワード2</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.important_keyword2}
                onChange={(e) => setFormData({ ...formData, important_keyword2: e.target.value })}
              >
                <option value="">選択してください</option>
                {importantKeywordOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">重要視したいキーワード3</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.important_keyword3}
                onChange={(e) => setFormData({ ...formData, important_keyword3: e.target.value })}
              >
                <option value="">選択してください</option>
                {importantKeywordOptions?.map((option) => (
                  <option key={option.id} value={option.value}>
                    {option.value}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {(!importantKeywordOptions || importantKeywordOptions.length === 0) && (
            <p className="text-xs text-gray-500">
              設定画面で選択肢を登録してください
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              {createMutation.isPending ? '生成中...' : '記事を生成'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

