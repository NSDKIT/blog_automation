import apiClient from './client'

export interface DataForSEOLabsResult {
  url: string
  payload: string
  headers?: { [key: string]: string }
  response_text?: string
  response_json?: any
  http_status_code?: number
  error?: string
}

export async function analyzeDataForSEOLabs(
  endpoint: string,
  params: {
    keyword?: string
    target?: string
    keywords?: string[]
    target1?: string
    target2?: string
    targets?: string[]
    category_codes?: number[]
    location_code?: number
    language_code?: string
  }
): Promise<DataForSEOLabsResult> {
  const searchParams = new URLSearchParams()
  searchParams.append('endpoint', endpoint)
  
  if (params.keyword) searchParams.append('keyword', params.keyword)
  if (params.target) searchParams.append('target', params.target)
  if (params.keywords) {
    params.keywords.forEach(kw => searchParams.append('keywords', kw))
  }
  if (params.target1) searchParams.append('target1', params.target1)
  if (params.target2) searchParams.append('target2', params.target2)
  if (params.targets) {
    params.targets.forEach(t => searchParams.append('targets', t))
  }
  if (params.category_codes) {
    params.category_codes.forEach(c => searchParams.append('category_codes', c.toString()))
  }
  if (params.location_code) searchParams.append('location_code', params.location_code.toString())
  if (params.language_code) searchParams.append('language_code', params.language_code)
  
  const response = await apiClient.post<DataForSEOLabsResult>(
    `/dataforseo-labs/analyze?${searchParams.toString()}`,
    {}
  )
  return response.data
}

