import apiClient from './client'

export interface UserImage {
  id: string
  keyword: string
  image_url: string
  alt_text: string | null
  created_at: string
  updated_at: string
}

export interface UserImageCreate {
  keyword: string
  image_url: string
  alt_text?: string
}

export interface UserImageUpdate {
  keyword?: string
  image_url?: string
  alt_text?: string
}

export const imagesApi = {
  getImages: async (keyword?: string) => {
    const params = keyword ? { keyword } : {}
    const response = await apiClient.get<UserImage[]>('/images', { params })
    return response.data
  },
  getImage: async (id: string) => {
    const response = await apiClient.get<UserImage>(`/images/${id}`)
    return response.data
  },
  createImage: async (data: UserImageCreate) => {
    const response = await apiClient.post<UserImage>('/images', data)
    return response.data
  },
  updateImage: async (id: string, data: UserImageUpdate) => {
    const response = await apiClient.put<UserImage>(`/images/${id}`, data)
    return response.data
  },
  deleteImage: async (id: string) => {
    await apiClient.delete(`/images/${id}`)
  },
}

