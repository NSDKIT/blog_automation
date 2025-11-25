"""
Shopify API クライアント
ユーザーごとのShopify設定を使用して記事を投稿
"""
import httpx
from typing import Dict, Optional
from app.supabase_db import get_setting_by_key


def get_shopify_config(user_id: str) -> Optional[Dict[str, str]]:
    """ユーザーのShopify設定を取得"""
    shop_domain = get_setting_by_key(user_id, "shopify_shop_domain")
    access_token = get_setting_by_key(user_id, "shopify_access_token")
    blog_id = get_setting_by_key(user_id, "shopify_blog_id")
    
    if not shop_domain or not access_token or not blog_id:
        return None
    
    return {
        "shop_domain": shop_domain,
        "access_token": access_token,
        "blog_id": blog_id
    }


async def publish_article_to_shopify(
    user_id: str,
    title: str,
    content: str,
    shopify_json: Optional[Dict] = None
) -> Optional[str]:
    """
    Shopifyに記事を投稿
    
    Args:
        user_id: ユーザーID
        title: 記事タイトル
        content: 記事本文（Markdown形式）
        shopify_json: Shopify形式のJSON（オプション）
    
    Returns:
        Shopify記事ID（投稿成功時）、None（失敗時）
    """
    config = get_shopify_config(user_id)
    if not config:
        raise ValueError("Shopify設定が完了していません。設定ページでShopify情報を登録してください。")
    
    # Shopify API URL
    shop_domain = config["shop_domain"]
    # myshopify.comが含まれていない場合は追加
    if not shop_domain.endswith(".myshopify.com"):
        if not shop_domain.endswith(".com"):
            shop_domain = f"{shop_domain}.myshopify.com"
    
    api_url = f"https://{shop_domain}/admin/api/2024-01/blogs/{config['blog_id']}/articles.json"
    
    # 記事データを準備
    if shopify_json:
        article_data = shopify_json.get("article", {})
    else:
        # デフォルトの記事データ
        article_data = {
            "title": title,
            "body_html": content,
            "author": "eightoon",
            "tags": "Column",
            "published": False,  # 下書きとして保存
            "status": "draft"
        }
    
    # Shopify APIに投稿
    headers = {
        "X-Shopify-Access-Token": config["access_token"],
        "Content-Type": "application/json"
    }
    
    payload = {
        "article": article_data
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("article") and result["article"].get("id"):
                return str(result["article"]["id"])
            return None
    except httpx.HTTPStatusError as e:
        raise Exception(f"Shopify API エラー: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"Shopify API リクエストエラー: {str(e)}")
    except Exception as e:
        raise Exception(f"Shopify投稿エラー: {str(e)}")

