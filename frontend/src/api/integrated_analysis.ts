import apiClient from './client'

export interface RelatedKeyword {
  keyword: string
  search_volume: number
  cpc: number
  competition: string
  competition_index: number
  difficulty: number
  difficulty_level: string
  priority_score: number
  recommended_rank: number
}

export interface MainKeyword {
  keyword: string
  search_volume: number
  cpc: number
  competition: string
  competition_index: number
  difficulty: number
  difficulty_level: string
}

export interface SummaryStats {
  immediate_attack: {
    count: number
    total_volume: number
  }
  medium_term: {
    count: number
    total_volume: number
  }
  long_term: {
    count: number
    total_volume: number
  }
}

export interface RecommendedStrategy {
  phase1: {
    keywords: RelatedKeyword[]
    estimated_traffic: number
    period: string
  }
}

export interface IntegratedAnalysisResult {
  main_keyword: MainKeyword | null
  related_keywords: RelatedKeyword[]
  summary_stats: SummaryStats
  recommended_strategy: RecommendedStrategy
  total_count: number
}

export async function analyzeIntegrated(
  keyword: string,
  relatedKeywordsLimit: number = 50,
  locationCode: number = 2840,
  languageCode: string = 'ja'
): Promise<IntegratedAnalysisResult> {
  const response = await apiClient.post<IntegratedAnalysisResult>(
    `/integrated-analysis/analyze?keyword=${encodeURIComponent(keyword)}&related_keywords_limit=${relatedKeywordsLimit}&location_code=${locationCode}&language_code=${encodeURIComponent(languageCode)}`,
    {}
  )
  return response.data
}

