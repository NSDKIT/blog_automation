import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '../api/settings'

interface ShopifySettings {
  shopify_shop_domain: string
  shopify_access_token: string
  shopify_blog_id: string
}

export default function Settings() {
  const queryClient = useQueryClient()
  const [shopifySettings, setShopifySettings] = useState<ShopifySettings>({
    shopify_shop_domain: '',
    shopify_access_token: '',
    shopify_blog_id: '',
  })

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.getSettings,
  })

  // 設定からShopify情報を読み込む
  useEffect(() => {
    if (settings) {
      const shopDomain = settings.find(s => s.key === 'shopify_shop_domain')?.value || ''
      const accessToken = settings.find(s => s.key === 'shopify_access_token')?.value || ''
      const blogId = settings.find(s => s.key === 'shopify_blog_id')?.value || ''
      
      setShopifySettings({
        shopify_shop_domain: shopDomain,
        shopify_access_token: accessToken,
        shopify_blog_id: blogId,
      })
    }
  }, [settings])

  const updateMutation = useMutation({
    mutationFn: settingsApi.updateSetting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      alert('設定を保存しました')
    },
  })

  const handleShopifySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // 3つの設定を保存
    updateMutation.mutate(
      { key: 'shopify_shop_domain', value: shopifySettings.shopify_shop_domain },
      {
        onSuccess: () => {
          updateMutation.mutate(
            { key: 'shopify_access_token', value: shopifySettings.shopify_access_token },
            {
              onSuccess: () => {
                updateMutation.mutate(
                  { key: 'shopify_blog_id', value: shopifySettings.shopify_blog_id }
                )
              },
            }
          )
        },
      }
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">設定</h1>

      {/* Shopify設定セクション */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Shopify設定</h2>
        <p className="text-sm text-gray-500 mb-4">
          記事をShopifyに投稿するために、以下の情報を設定してください。
        </p>
        <form onSubmit={handleShopifySubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Shop Domain
            </label>
            <input
              type="text"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={shopifySettings.shopify_shop_domain}
              onChange={(e) => setShopifySettings({ ...shopifySettings, shopify_shop_domain: e.target.value })}
              placeholder="例: your-shop.myshopify.com または your-shop"
            />
            <p className="mt-1 text-xs text-gray-500">
              .myshopify.com は自動的に追加されます
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Access Token
            </label>
            <input
              type="password"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={shopifySettings.shopify_access_token}
              onChange={(e) => setShopifySettings({ ...shopifySettings, shopify_access_token: e.target.value })}
              placeholder="Shopify Admin API Access Token"
            />
            <p className="mt-1 text-xs text-gray-500">
              Shopify管理画面 &gt; Settings &gt; Apps and sales channels &gt; Develop apps から取得
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Blog ID
            </label>
            <input
              type="text"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={shopifySettings.shopify_blog_id}
              onChange={(e) => setShopifySettings({ ...shopifySettings, shopify_blog_id: e.target.value })}
              placeholder="例: 123456789"
            />
            <p className="mt-1 text-xs text-gray-500">
              Shopify管理画面 &gt; Online Store &gt; Blog posts から確認
            </p>
          </div>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {updateMutation.isPending ? '保存中...' : 'Shopify設定を保存'}
          </button>
        </form>
      </div>

      {/* その他の設定セクション */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">その他の設定</h2>
        {settings && settings.filter(s => !s.key.startsWith('shopify_')).length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {settings
              .filter(s => !s.key.startsWith('shopify_'))
              .map((setting) => (
                <li key={setting.id} className="py-4">
                  <div className="flex justify-between">
                    <span className="font-medium text-gray-900">{setting.key}</span>
                    <span className="text-gray-500">
                      {setting.key.includes('token') || setting.key.includes('key') || setting.key.includes('password')
                        ? '••••••••'
                        : setting.value}
                    </span>
                  </div>
                </li>
              ))}
          </ul>
        ) : (
          <p className="text-gray-500">その他の設定がありません</p>
        )}
      </div>
    </div>
  )
}

