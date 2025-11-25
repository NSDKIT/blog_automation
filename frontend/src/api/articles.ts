import apiClient from './client'

export interface Article {
  id: string
  keyword: string
  target: string
  article_type: string
  title: string | null
  content: string | null
  shopify_article_id: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface ArticleCreate {
  keyword: string
  target: string
  article_type: string
  used_type1?: string
  used_type2?: string
  used_type3?: string
  prompt?: string
  important_keyword1?: string
  important_keyword2?: string
  important_keyword3?: string
  sheet_id: string
}

export interface ArticleUpdate {
  title?: string
  content?: string
  status?: string
}

export const articlesApi = {
  getArticles: async () => {
    const response = await apiClient.get<Article[]>('/articles')
    return response.data
  },
  getArticle: async (id: string) => {
    const response = await apiClient.get<Article>(`/articles/${id}`)
    return response.data
  },
  createArticle: async (data: ArticleCreate) => {
    const response = await apiClient.post<Article>('/articles', data)
    return response.data
  },
  updateArticle: async (id: string, data: ArticleUpdate) => {
    const response = await apiClient.put<Article>(`/articles/${id}`, data)
    return response.data
  },
  deleteArticle: async (id: string) => {
    await apiClient.delete(`/articles/${id}`)
  },
  publishArticle: async (id: string) => {
    const response = await apiClient.post(`/articles/${id}/publish`)
    return response.data
  },
}

