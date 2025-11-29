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

