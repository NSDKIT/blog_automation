import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '../api/settings'

export default function Settings() {
  const queryClient = useQueryClient()
  const [key, setKey] = useState('')
  const [value, setValue] = useState('')

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.getSettings,
  })

  const updateMutation = useMutation({
    mutationFn: settingsApi.updateSetting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      setKey('')
      setValue('')
      alert('設定を更新しました')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate({ key, value })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">設定</h1>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">設定一覧</h2>
        {settings && settings.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {settings.map((setting) => (
              <li key={setting.id} className="py-4">
                <div className="flex justify-between">
                  <span className="font-medium text-gray-900">{setting.key}</span>
                  <span className="text-gray-500">{setting.value}</span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">設定がありません</p>
        )}
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">新規設定</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              キー
            </label>
            <input
              type="text"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="例: OPENAI_API_KEY"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              値
            </label>
            <input
              type="text"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="設定値"
            />
          </div>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {updateMutation.isPending ? '保存中...' : '保存'}
          </button>
        </form>
      </div>
    </div>
  )
}

