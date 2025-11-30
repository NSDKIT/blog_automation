import apiClient from './client'

export interface IntegratedAnalysisResult {
  id: string
  user_id: string
  keyword: string
  location_code: number
  language_code: string
  main_keyword?: any
  related_keywords?: any[]
  summary_stats?: any
  recommended_strategy?: any
  created_at: string
  updated_at: string
}

export interface IntegratedAnalysisCreate {
  keyword: string
  location_code?: number
  language_code?: string
  main_keyword?: any
  related_keywords?: any[]
  summary_stats?: any
  recommended_strategy?: any
}

export async function createIntegratedAnalysis(
  data: IntegratedAnalysisCreate
): Promise<IntegratedAnalysisResult> {
  const response = await apiClient.post<IntegratedAnalysisResult>(
    '/integrated-analysis-results/',
    data
  )
  return response.data
}

export async function listIntegratedAnalyses(): Promise<IntegratedAnalysisResult[]> {
  const response = await apiClient.get<IntegratedAnalysisResult[]>(
    '/integrated-analysis-results/'
  )
  return response.data
}

export async function getIntegratedAnalysis(
  id: string
): Promise<IntegratedAnalysisResult> {
  const response = await apiClient.get<IntegratedAnalysisResult>(
    `/integrated-analysis-results/${id}`
  )
  return response.data
}

export async function deleteIntegratedAnalysis(id: string): Promise<void> {
  await apiClient.delete(`/integrated-analysis-results/${id}`)
}

