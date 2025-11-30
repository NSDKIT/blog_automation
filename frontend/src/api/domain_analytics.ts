import apiClient from './client'

export interface DomainAnalyticsResult {
  keyword?: string
  target?: string
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

export async function analyzeDomainAnalytics(
  keyword?: string,
  target?: string,
  locationCode: number = 2840,
  languageCode: string = 'ja'
): Promise<DomainAnalyticsResult> {
  const params = new URLSearchParams()
  if (keyword) params.append('keyword', keyword)
  if (target) params.append('target', target)
  params.append('location_code', locationCode.toString())
  params.append('language_code', languageCode)
  
  const response = await apiClient.post<DomainAnalyticsResult>(
    `/domain-analytics/analyze?${params.toString()}`,
    {}
  )
  return response.data
}

