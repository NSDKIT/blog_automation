import apiClient from './client'

export interface SERPResult {
  keyword: string
  location_code: number
  language_code: string
  results: Array<{
    url: string
    payload: string
    headers?: { [key: string]: string }
    response_text?: string
    response_json?: any
    http_status_code?: number
    error?: string
  }>
  seo_analysis?: {
    headings_analysis: {
      h1_patterns: { [key: string]: number }
      h2_patterns: { [key: string]: number }
      h3_patterns: { [key: string]: number }
      avg_title_length: number
      min_title_length: number
      max_title_length: number
      recommended_title_length: {
        min: number
        max: number
      }
    }
    titles_analysis: {
      titles: string[]
      keyword_patterns: Array<{
        title: string
        length: number
        has_number: boolean
        has_question: boolean
      }>
      emotion_words: { [key: string]: number }
      action_words: { [key: string]: number }
      title_suggestions: Array<{
        pattern: string
        example: string
        score: number
      }>
    }
    faq_items: Array<{
      question: string
      answer: string
      type: string
    }>
    keyword_optimization?: {
      related_keywords: {
        related_keywords: Array<{
          keyword: string
          type: string
          priority: string
          frequency?: number
        }>
        total_count: number
      }
      keyword_density: {
        average_density: number
        recommended_density: {
          min: number
          max: number
        }
        keyword_positions: Array<{
          in_title: boolean
          in_snippet: boolean
          density: number
        }>
        recommendation: string
      }
    }
    competitor_analysis?: {
      competitors: Array<{
        position: number
        title: string
        snippet: string
        url: string
        features: string[]
        topics: string[]
        title_length: number
        snippet_length: number
      }>
      common_topics: string[]
      rare_topics: string[]
      content_gaps: string[]
      differentiation_strategy: {
        focus_areas: string[]
        must_include: string[]
        recommendation: string
      }
    }
    search_intent?: {
      dominant_intent: string
      intent_scores: {
        informational: number
        commercial: number
        transactional: number
        navigational: number
      }
      recommended_article_type: string
      confidence: number
    }
    structured_data?: {
      suggestions: Array<{
        type: string
        priority: string
        reason: string
        example?: any
      }>
      has_featured_snippet: boolean
      needs_faq_schema: boolean
      needs_article_schema: boolean
    }
    prompt_generation?: {
      prompt: string
      recommended_headings: string[]
      faq_questions: string[]
      recommended_keywords: string[]
      focus_areas: string[]
    }
  }
}

export async function analyzeSERP(
  keyword: string,
  locationCode: number,
  languageCode: string
): Promise<SERPResult> {
  const response = await apiClient.post<SERPResult>(
    `/serp-analysis/analyze?keyword=${encodeURIComponent(keyword)}&location_code=${locationCode}&language_code=${encodeURIComponent(languageCode)}`,
    {}
  )
  return response.data
}

