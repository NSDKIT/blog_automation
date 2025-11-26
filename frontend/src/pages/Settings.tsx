import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '../api/settings'
import { imagesApi } from '../api/images'
import { optionsApi } from '../api/options'

interface ShopifySettings {
  shopify_shop_domain: string
  shopify_access_token: string
  shopify_blog_id: string
}

interface WordPressSettings {
  wordpress_url: string
  wordpress_user: string
  wordpress_pass: string
}


function ImageKeywordSection() {
  const queryClient = useQueryClient()
  const [keyword, setKeyword] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [altText, setAltText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadMethod, setUploadMethod] = useState<'url' | 'file'>('file')

  const { data: images } = useQuery({
    queryKey: ['images'],
    queryFn: () => imagesApi.getImages(),
  })

  const createMutation = useMutation({
    mutationFn: async (data: { keyword: string; image_url?: string; alt_text?: string; file?: File }) => {
      if (data.file) {
        // ファイルアップロード
        const formData = new FormData()
        formData.append('keyword', data.keyword)
        formData.append('file', data.file)
        if (data.alt_text) {
          formData.append('alt_text', data.alt_text)
        }
        
        const response = await fetch(`${import.meta.env.VITE_API_URL}/images`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage') || '{}').state?.token : ''}`
          },
          body: formData
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || '画像のアップロードに失敗しました')
        }
        
        return response.json()
      } else {
        // URL指定
        return imagesApi.createImage({
          keyword: data.keyword,
          image_url: data.image_url!,
          alt_text: data.alt_text
        })
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['images'] })
      setKeyword('')
      setImageUrl('')
      setAltText('')
      setSelectedFile(null)
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
    
    if (uploadMethod === 'file' && !selectedFile) {
      alert('画像ファイルを選択してください')
      return
    }
    
    if (uploadMethod === 'url' && !imageUrl) {
      alert('画像URLを入力してください')
      return
    }
    
    createMutation.mutate({
      keyword,
      image_url: uploadMethod === 'url' ? imageUrl : undefined,
      alt_text: altText || undefined,
      file: uploadMethod === 'file' ? selectedFile || undefined : undefined,
    })
  }
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // ファイルサイズチェック（10MB以下）
      if (file.size > 10 * 1024 * 1024) {
        alert('ファイルサイズは10MB以下にしてください')
        return
      }
      // 画像ファイルかチェック
      if (!file.type.startsWith('image/')) {
        alert('画像ファイルを選択してください')
        return
      }
      setSelectedFile(file)
    }
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
            アップロード方法
          </label>
          <div className="flex space-x-4 mb-3">
            <label className="flex items-center">
              <input
                type="radio"
                name="uploadMethod"
                value="file"
                checked={uploadMethod === 'file'}
                onChange={(e) => setUploadMethod(e.target.value as 'file' | 'url')}
                className="mr-2"
              />
              ファイルをアップロード
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="uploadMethod"
                value="url"
                checked={uploadMethod === 'url'}
                onChange={(e) => setUploadMethod(e.target.value as 'file' | 'url')}
                className="mr-2"
              />
              URLを指定
            </label>
          </div>
          
          {uploadMethod === 'file' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                画像ファイル <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
              {selectedFile && (
                <div className="mt-2">
                  <p className="text-sm text-gray-600">選択中: {selectedFile.name}</p>
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="プレビュー"
                    className="mt-2 max-w-xs h-32 object-cover rounded"
                  />
                </div>
              )}
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                画像URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                required={uploadMethod === 'url'}
                className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://example.com/image.jpg"
              />
            </div>
          )}
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
  const [wordpressSettings, setWordpressSettings] = useState<WordPressSettings>({
    wordpress_url: '',
    wordpress_user: '',
    wordpress_pass: '',
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

      const wpUrl = settings.find(s => s.key === 'wordpress_url')?.value || ''
      const wpUser = settings.find(s => s.key === 'wordpress_user')?.value || ''
      const wpPass = settings.find(s => s.key === 'wordpress_pass')?.value || ''
      
      setWordpressSettings({
        wordpress_url: wpUrl,
        wordpress_user: wpUser,
        wordpress_pass: wpPass,
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

  const handleWordPressSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // 3つの設定を保存
    updateMutation.mutate(
      { key: 'wordpress_url', value: wordpressSettings.wordpress_url },
      {
        onSuccess: () => {
          updateMutation.mutate(
            { key: 'wordpress_user', value: wordpressSettings.wordpress_user },
            {
              onSuccess: () => {
                updateMutation.mutate(
                  { key: 'wordpress_pass', value: wordpressSettings.wordpress_pass }
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

      {/* WordPress設定セクション */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">WordPress設定</h2>
        <p className="text-sm text-gray-500 mb-4">
          記事をWordPressに投稿するために、以下の情報を設定してください。
        </p>
        <form onSubmit={handleWordPressSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              WordPressサイトURL <span className="text-red-500">*</span>
            </label>
            <input
              type="url"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={wordpressSettings.wordpress_url}
              onChange={(e) => setWordpressSettings({ ...wordpressSettings, wordpress_url: e.target.value })}
              placeholder="例: https://nsdkit0224-msvag.wpcomstaging.com"
            />
            <p className="mt-1 text-xs text-gray-500">
              WordPressサイトのベースURL（/wp-json/wp/v2/postsは自動的に追加されます）
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ユーザー名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={wordpressSettings.wordpress_user}
              onChange={(e) => setWordpressSettings({ ...wordpressSettings, wordpress_user: e.target.value })}
              placeholder="例: nsdkit0224"
            />
            <p className="mt-1 text-xs text-gray-500">
              サイトのダッシュボードで確認したユーザー名
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              アプリケーションパスワード <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              required
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              value={wordpressSettings.wordpress_pass}
              onChange={(e) => setWordpressSettings({ ...wordpressSettings, wordpress_pass: e.target.value })}
              placeholder="Application Passwordsで設定されたパスワード"
            />
            <p className="mt-1 text-xs text-gray-500">
              Application Passwordsで設定されたパスワード（例: sPVm AtAS 8Uzu B4x1 FvwP AnMc）
            </p>
          </div>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {updateMutation.isPending ? '保存中...' : 'WordPress設定を保存'}
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

      {/* 選択肢登録セクション */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">選択肢登録</h2>
        <p className="text-sm text-gray-500 mb-4">
          記事作成時に使用する選択肢を登録してください。
        </p>
        <UserOptionsSection />
      </div>
    </div>
  )
}

function UserOptionsSection() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<'target' | 'article_type' | 'used_type' | 'important_keyword'>('target')
  const [newValue, setNewValue] = useState('')

  const { data: options } = useQuery({
    queryKey: ['options', selectedCategory],
    queryFn: () => optionsApi.getOptions(selectedCategory),
  })

  const createMutation = useMutation({
    mutationFn: optionsApi.createOption,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['options'] })
      setNewValue('')
      alert('選択肢を登録しました')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: optionsApi.deleteOption,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['options'] })
      alert('選択肢を削除しました')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newValue.trim()) {
      alert('値を入力してください')
      return
    }
    createMutation.mutate({
      category: selectedCategory,
      value: newValue.trim(),
    })
  }

  const categoryLabels = {
    target: 'ターゲット層',
    article_type: '記事の種類',
    used_type: '使用シーン',
    important_keyword: '重要視したいキーワード',
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          カテゴリ
        </label>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as typeof selectedCategory)}
          className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        >
          <option value="target">ターゲット層</option>
          <option value="article_type">記事の種類</option>
          <option value="used_type">使用シーン</option>
          <option value="important_keyword">重要視したいキーワード</option>
        </select>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            新しい選択肢を追加
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              placeholder={`${categoryLabels[selectedCategory]}の選択肢を入力`}
              className="flex-1 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
            >
              {createMutation.isPending ? '登録中...' : '追加'}
            </button>
          </div>
        </div>
      </form>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          登録済み選択肢: {categoryLabels[selectedCategory]}
        </h3>
        {options && options.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {options.map((option) => (
              <li key={option.id} className="py-3 flex justify-between items-center">
                <span className="text-gray-900">{option.value}</span>
                <button
                  onClick={() => {
                    if (confirm('この選択肢を削除しますか？')) {
                      deleteMutation.mutate(option.id)
                    }
                  }}
                  disabled={deleteMutation.isPending}
                  className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs font-medium disabled:opacity-50"
                >
                  削除
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">登録された選択肢がありません</p>
        )}
      </div>
    </div>
  )
}

