import apiClient from './client'

export interface Setting {
  id: string
  key: string
  value: string
  is_masked: boolean
  created_at: string
  updated_at: string
}

export interface SettingUpdate {
  key: string
  value: string
}

export const settingsApi = {
  getSettings: async () => {
    const response = await apiClient.get<Setting[]>('/settings')
    return response.data
  },
  updateSetting: async (data: SettingUpdate) => {
    const response = await apiClient.put<Setting>('/settings', data)
    return response.data
  },
}
