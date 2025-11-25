import apiClient from './client'

export interface UserOption {
  id: string
  category: string
  value: string
  display_order: number
  created_at: string
  updated_at: string
}

export interface UserOptionCreate {
  category: 'target' | 'article_type' | 'used_type' | 'important_keyword'
  value: string
  display_order?: number
}

export interface UserOptionUpdate {
  value?: string
  display_order?: number
}

export const optionsApi = {
  getOptions: async (category: string) => {
    const response = await apiClient.get<UserOption[]>('/options', {
      params: { category }
    })
    return response.data
  },
  getOption: async (id: string) => {
    const response = await apiClient.get<UserOption>(`/options/${id}`)
    return response.data
  },
  createOption: async (data: UserOptionCreate) => {
    const response = await apiClient.post<UserOption>('/options', data)
    return response.data
  },
  updateOption: async (id: string, data: UserOptionUpdate) => {
    const response = await apiClient.put<UserOption>(`/options/${id}`, data)
    return response.data
  },
  deleteOption: async (id: string) => {
    await apiClient.delete(`/options/${id}`)
  },
}

