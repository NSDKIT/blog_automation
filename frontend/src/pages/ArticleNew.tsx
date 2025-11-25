import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { articlesApi, ArticleCreate } from '../api/articles'

const TARGET_OPTIONS = [
  'インドアワーカー',
  'ゲーマー',
  'クリエイター',
  'リモートワーカー',
  '眼鏡愛用者',
]

const ARTICLE_TYPE_OPTIONS = [
  'ハウツー系:「〜する方法」「〜のコツ」「〜の選び方」',
  '体験・レビュー系:「実際に使ってみた」「〜してみたら」「使用感レポート」',
  '比較・解説系:「〜と〜の違い」「徹底比較」「プロが解説」',
  'トレンド・話題系:「今話題の」「最新トレンド」',
  '問題解決系: 「〜でお悩みの方へ」「〜を解決する」「〜の悩み解消」',
  '特徴・メリット系: 「〜がすごい理由」「〜の魅力」「〜のメリット」',
  'ライフスタイル系: 「〜な生活」「〜のある暮らし」「〜でライフスタイル向上」',
  '数字・リスト系:「5つのポイント」「10の理由」「3つの秘密」',
  'Eightoon宣伝系',
]

const USED_TYPE_OPTIONS = ['指定なし', '室内', '仕事', 'デート', '友達と遊ぶ', 'クラブ']

const IMPORTANT_KEYWORD_OPTIONS = [
  'EIGHTOON',
  'インドアライフ/インドアワーク',
  'ブルーライトカット',
  '鯖江',
  'βチタニウム',
  'ゲーミング',
  '職人技術',
  '快適性',
]

export default function ArticleNew() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<ArticleCreate>({
    keyword: '',
    target: '',
    article_type: '',
    used_type1: '指定なし',
    used_type2: '',
    used_type3: '',
    prompt: '',
    important_keyword1: '',
    important_keyword2: '',
    important_keyword3: '',
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
              {TARGET_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
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
              {ARTICLE_TYPE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">使用シーン1</label>
              <select
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.used_type1}
                onChange={(e) => setFormData({ ...formData, used_type1: e.target.value })}
              >
                {USED_TYPE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
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
                {USED_TYPE_OPTIONS.filter((o) => o !== '指定なし').map((option) => (
                  <option key={option} value={option}>
                    {option}
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
                {USED_TYPE_OPTIONS.filter((o) => o !== '指定なし').map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>

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
                {IMPORTANT_KEYWORD_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
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
                {IMPORTANT_KEYWORD_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
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
                {IMPORTANT_KEYWORD_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
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

