import apiClient from './client'

export interface UserRegister {
  email: string
  password: string
  name: string
}

export interface UserLogin {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  name: string
  role: string
}

export const authApi = {
  register: async (data: UserRegister) => {
    const response = await apiClient.post<User>('/auth/register', data)
    return response.data
  },
  login: async (data: UserLogin) => {
    const response = await apiClient.post<Token>('/auth/login', data)
    return response.data
  },
  getMe: async () => {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },
}

