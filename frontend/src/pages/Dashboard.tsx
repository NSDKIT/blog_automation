import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { articlesApi } from '../api/articles'

export default function Dashboard() {
  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles'],
    queryFn: articlesApi.getArticles,
  })

  if (isLoading) {
    return <div className="text-center py-12">読み込み中...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">記事一覧</h1>
        <Link
          to="/articles/new"
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
        >
          新規記事生成
        </Link>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {articles && articles.length > 0 ? (
            articles.map((article) => (
              <li key={article.id}>
                <Link
                  to={`/articles/${article.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-indigo-600 truncate">
                          {article.title || article.keyword}
                        </p>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          article.status === 'completed' ? 'bg-green-100 text-green-800' :
                          article.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                          article.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {article.status}
                        </span>
                      </div>
                      <div className="mt-2 flex flex-col text-sm text-gray-500">
                        <p>
                          キーワード: {article.keyword} | ターゲット: {article.target} | 種類: {article.article_type}
                        </p>
                        {article.status === 'failed' && (
                          <span className="mt-1 text-red-600">
                            エラー: {article.error_message ?? '詳細は記事詳細画面をご確認ください。'}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-5 flex-shrink-0">
                      <p className="text-sm text-gray-500">
                        {new Date(article.created_at).toLocaleDateString('ja-JP')}
                      </p>
                    </div>
                  </div>
                </Link>
              </li>
            ))
          ) : (
            <li className="px-4 py-8 text-center text-gray-500">
              記事がありません
            </li>
          )}
        </ul>
      </div>
    </div>
  )
}

