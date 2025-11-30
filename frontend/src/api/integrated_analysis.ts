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
  locationCode: number = 2840,
  languageCode: string = 'ja'
): Promise<IntegratedAnalysisResult> {
  try {
    const response = await apiClient.post<IntegratedAnalysisResult>(
      `/integrated-analysis/analyze?keyword=${encodeURIComponent(keyword)}&location_code=${locationCode}&language_code=${encodeURIComponent(languageCode)}`,
      {},
      {
        timeout: 180000, // 3分のタイムアウト（複数API呼び出しのため）
      }
    )
    return response.data
  } catch (error: any) {
    // より詳細なエラーメッセージを提供
    if (error.code === 'ECONNABORTED') {
      throw new Error('リクエストがタイムアウトしました。処理に時間がかかっている可能性があります。')
    } else if (error.response) {
      // サーバーからのエラーレスポンス
      const errorMessage = error.response.data?.detail || error.response.data?.message || error.message
      throw new Error(`サーバーエラー: ${errorMessage}`)
    } else if (error.request) {
      // リクエストは送信されたが、レスポンスが受信されなかった
      throw new Error('サーバーに接続できませんでした。ネットワーク接続を確認してください。')
    } else {
      // リクエストの設定中にエラーが発生
      throw new Error(`リクエストエラー: ${error.message}`)
    }
  }
}

