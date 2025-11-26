"""
WordPress REST API クライアント
提供コードと同じ形式でWordPressに投稿
"""
import json
import requests
from datetime import datetime
from typing import Optional, Dict
from app.supabase_db import get_setting_by_key


def get_wordpress_config(user_id: str) -> Optional[Dict[str, str]]:
    """ユーザーのWordPress設定を取得"""
    wp_url = get_setting_by_key(user_id, "wordpress_url")
    wp_user = get_setting_by_key(user_id, "wordpress_user")
    wp_pass = get_setting_by_key(user_id, "wordpress_pass")
    
    if not wp_url or not wp_user or not wp_pass:
        return None
    
    # URLにhttps://またはhttp://が含まれていない場合は自動的にhttps://を追加
    base_url = wp_url.strip()
    if not base_url.startswith(('http://', 'https://')):
        base_url = f"https://{base_url}"
    
    # 末尾のスラッシュを削除
    base_url = base_url.rstrip('/')
    
    # URLに/wp-json/wp/v2/postsが含まれていない場合は自動的に追加
    if '/wp-json/wp/v2/posts' not in base_url:
        api_url = f"{base_url}/wp-json/wp/v2/posts"
    else:
        api_url = base_url
    
    return {
        "url": api_url,
        "user": wp_user,
        "pass": wp_pass
    }


def publish_to_wordpress(
    wp_url: str,
    wp_user: str,
    wp_pass: str,
    title: str,
    content: str,
    slug: Optional[str] = None,
    status: str = "draft"
) -> requests.Response:
    """
    提供コードと同じ形式でWordPressに投稿
    
    Args:
        wp_url: WordPress REST API URL
        wp_user: WordPressユーザー名
        wp_pass: WordPressアプリケーションパスワード
        title: 記事タイトル
        content: 記事本文
        slug: スラッグ（オプション）
        status: ステータス（デフォルト: "draft"）
    
    Returns:
        requests.Response: WordPress APIからのレスポンス
    """
    payload = {
        "status": status,
        "title": title,
        "content": content,
        "date": datetime.now().isoformat(),
    }
    
    if slug:
        payload["slug"] = slug
    
    res = requests.post(
        wp_url,
        data=json.dumps(payload),
        headers={"Content-type": "application/json"},
        auth=(wp_user, wp_pass)
    )
    
    return res

