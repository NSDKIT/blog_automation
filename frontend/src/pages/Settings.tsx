import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '../api/settings'
import { imagesApi } from '../api/images'

interface ShopifySettings {
  shopify_shop_domain: string
  shopify_access_token: string
  shopify_blog_id: string
}

function ImageKeywordSection() {
  const queryClient = useQueryClient()
  const [keyword, setKeyword] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [altText, setAltText] = useState('')

  const { data: images } = useQuery({
    queryKey: ['images'],
    queryFn: () => imagesApi.getImages(),
  })

  const createMutation = useMutation({
    mutationFn: imagesApi.createImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] })
      setKeyword('')
      setImageUrl('')
      setAltText('')
      alert('画像を登録しました')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: imagesApi.deleteImage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] })
      alert('画像を削除しました')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      keyword,
      image_url: imageUrl,
      alt_text: altText || undefined,
    })
  }

  // キーワードごとにグループ化
  const imagesByKeyword = images?.reduce((acc, img) => {
    if (!acc[img.keyword]) {
      acc[img.keyword] = []
    }
    acc[img.keyword].push(img)
    return acc
  }, {} as Record<string, typeof images>) || {}

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            キーワード <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            required
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="例: メガネ"
          />
          <p className="mt-1 text-xs text-gray-500">
            記事生成時に使用するキーワードを入力してください
          </p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            画像URL <span className="text-red-500">*</span>
          </label>
          <input
            type="url"
            required
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            placeholder="https://example.com/image.jpg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Alt テキスト（オプション）
          </label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={altText}
            onChange={(e) => setAltText(e.target.value)}
            placeholder="画像の説明"
          />
        </div>
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
        >
          {createMutation.isPending ? '登録中...' : '画像を登録'}
        </button>
      </form>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">登録済み画像</h3>
        {Object.keys(imagesByKeyword).length > 0 ? (
          <div className="space-y-6">
            {Object.entries(imagesByKeyword).map(([kw, imgs]) => (
              <div key={kw} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">キーワード: {kw}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {imgs.map((img) => (
                    <div key={img.id} className="border border-gray-200 rounded p-3">
                      <img
                        src={img.image_url}
                        alt={img.alt_text || img.keyword}
                        className="w-full h-32 object-cover rounded mb-2"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x200?text=Image+Not+Found'
                        }}
                      />
                      <p className="text-xs text-gray-500 mb-2 truncate">{img.alt_text || '説明なし'}</p>
                      <button
                        onClick={() => {
                          if (confirm('この画像を削除しますか？')) {
                            deleteMutation.mutate(img.id)
                          }
                        }}
                        disabled={deleteMutation.isPending}
                        className="w-full bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-medium disabled:opacity-50"
                      >
                        削除
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">登録された画像がありません</p>
        )}
      </div>
    </div>
  )
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

      {/* 画像キーワード登録セクション */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">画像キーワード登録</h2>
        <p className="text-sm text-gray-500 mb-4">
          記事生成時に使用する画像をキーワードごとに登録してください。
        </p>
        <ImageKeywordSection />
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

