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
    search_intent: '情報収集',
    target_location: 'Japan',
    device_type: 'mobile',
    secondary_keywords: [],
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
      // キーワード分析中の画面を表示するため、直接キーワード選択ページにリダイレクト
      navigate(`/articles/${data.id}/keywords`)
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

          {/* SEO関連設定 */}
          <div className="border-t pt-6 mt-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">SEO設定</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  検索意図
                </label>
                <select
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  value={formData.search_intent}
                  onChange={(e) => setFormData({ ...formData, search_intent: e.target.value })}
                >
                  <option value="情報収集">情報収集</option>
                  <option value="購買検討">購買検討</option>
                  <option value="比較検討">比較検討</option>
                  <option value="問題解決">問題解決</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  検索地域
                </label>
                <select
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  value={formData.target_location}
                  onChange={(e) => setFormData({ ...formData, target_location: e.target.value })}
                >
                  <option value="Japan">日本</option>
                  <option value="Tokyo">東京</option>
                  <option value="Osaka">大阪</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  デバイスタイプ
                </label>
                <select
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  value={formData.device_type}
                  onChange={(e) => setFormData({ ...formData, device_type: e.target.value })}
                >
                  <option value="mobile">モバイル</option>
                  <option value="desktop">デスクトップ</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">
                サブキーワード（カンマ区切り）
              </label>
              <input
                type="text"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="キーワード1, キーワード2, キーワード3"
                value={formData.secondary_keywords?.join(', ') || ''}
                onChange={(e) => {
                  const keywords = e.target.value.split(',').map(k => k.trim()).filter(k => k)
                  setFormData({ ...formData, secondary_keywords: keywords })
                }}
              />
              <p className="mt-1 text-xs text-gray-500">
                メインキーワード以外の関連キーワードを入力してください
              </p>
            </div>
          </div>

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

