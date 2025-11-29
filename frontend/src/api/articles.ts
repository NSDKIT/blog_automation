import apiClient from './client'

export interface Article {
  id: string
  keyword: string
  target: string
  article_type: string
  title: string | null
  content: string | null
  shopify_article_id: string | null
  error_message: string | null
  status: string
  created_at: string
  updated_at: string
  // SEO関連フィールド
  meta_title?: string | null
  meta_description?: string | null
  search_intent?: string | null
  target_location?: string | null
  device_type?: string | null
  serp_data?: any
  serp_headings_analysis?: any
  serp_common_patterns?: any
  serp_faq_items?: string[] | null
  keyword_volume_data?: any
  related_keywords?: any
  keyword_difficulty?: any
  subtopics?: string[] | null
  content_structure?: any
  structured_data?: any
  best_keywords?: any  // 最適なキーワードリスト（スコアリング済み）
  analyzed_keywords?: any  // 分析済みキーワードリスト（全100個）
  selected_keywords?: string[] | null  // ユーザーが選択したキーワード
  selected_keywords_data?: any  // 選択されたキーワードの詳細データ
  keyword_analysis_progress?: {
    status_check?: boolean
    openai_generation?: boolean
    dataforseo_fetch?: boolean
    scoring_completed?: boolean
    current_step?: string
    error_message?: string | null
  } | null  // キーワード分析の進捗状況
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
  sheet_id?: string  // 後方互換性のため残すが、使用しない
  // SEO関連フィールド
  search_intent?: string
  target_location?: string
  device_type?: string
  secondary_keywords?: string[]
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
  publishToWordPress: async (id: string) => {
    const response = await apiClient.post(`/articles/${id}/publish-wordpress`)
    return response.data
  },
  selectKeywords: async (id: string, selectedKeywords: string[]) => {
    const response = await apiClient.post(`/articles/${id}/select-keywords`, {
      selected_keywords: selectedKeywords
    })
    return response.data
  },
  startKeywordAnalysis: async (id: string) => {
    const response = await apiClient.post(`/articles/${id}/start-keyword-analysis`)
    return response.data
  },
}

