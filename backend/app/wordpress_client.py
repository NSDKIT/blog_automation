"""
WordPress REST API クライアント
ユーザーごとのWordPress設定を使用して記事を投稿
"""
import httpx
import base64
import mimetypes
from typing import Dict, Optional
from app.supabase_db import get_setting_by_key


def get_wordpress_config(user_id: str) -> Optional[Dict[str, str]]:
    """ユーザーのWordPress設定を取得"""
    site_url = get_setting_by_key(user_id, "wordpress_site_url")
    username = get_setting_by_key(user_id, "wordpress_username")
    app_password = get_setting_by_key(user_id, "wordpress_app_password")
    
    if not site_url or not username or not app_password:
        return None
    
    return {
        "site_url": site_url,
        "username": username,
        "app_password": app_password
    }


async def upload_image_to_wordpress(
    user_id: str,
    image_url: str,
    image_filename: str = "image.jpg"
) -> Optional[int]:
    """
    WordPressに画像をアップロード
    
    Args:
        user_id: ユーザーID
        image_url: 画像のURL
        image_filename: 画像ファイル名
    
    Returns:
        画像ID（アップロード成功時）、None（失敗時）
    """
    config = get_wordpress_config(user_id)
    if not config:
        raise ValueError("WordPress設定が完了していません。設定ページでWordPress情報を登録してください。")
    
    # 画像をダウンロード
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            image_response = await client.get(image_url)
            image_response.raise_for_status()
            image_data = image_response.content
    except Exception as e:
        raise Exception(f"画像のダウンロードに失敗しました: {str(e)}")
    
    # MIMEタイプを取得
    mime_type, _ = mimetypes.guess_type(image_filename)
    if not mime_type:
        mime_type = "image/jpeg"
    
    # WordPress REST API URL
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/media"
    
    # Basic認証ヘッダー
    credentials = f"{config['username']}:{config['app_password']}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Disposition": f'attachment; filename="{image_filename}"',
        "Content-Type": mime_type,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                content=image_data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("id"):
                return result["id"]
            return None
    except httpx.HTTPStatusError as e:
        error_detail = ""
        if e.response.status_code == 404:
            error_detail = (
                f"WordPress REST APIエンドポイントが見つかりません (404)。\n"
                f"確認事項:\n"
                f"1. WordPressサイトURLが正しいか確認してください（例: https://example.com）\n"
                f"2. WordPress.comのサイトを使用している場合、通常のWordPress REST APIは利用できません。\n"
                f"   自己ホスト型のWordPressサイト（WordPress.org）を使用してください。\n"
                f"3. REST APIが有効になっているか確認してください。\n"
                f"   試しにブラウザで {api_url} にアクセスして確認してください。\n"
                f"4. アプリケーションパスワードが正しいか確認してください。\n"
                f"\nエラー詳細: {e.response.text[:500]}"
            )
        else:
            error_detail = f"WordPress API エラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_detail)
    except httpx.RequestError as e:
        raise Exception(f"WordPress API リクエストエラー: {str(e)}")
    except Exception as e:
        raise Exception(f"WordPress画像アップロードエラー: {str(e)}")


async def publish_article_to_wordpress(
    user_id: str,
    title: str,
    content: str,
    slug: Optional[str] = None,
    featured_media_id: Optional[int] = None,
    status: str = "publish",
    comment_status: str = "closed"
) -> Optional[int]:
    """
    WordPressに記事を投稿
    
    Args:
        user_id: ユーザーID
        title: 記事タイトル
        content: 記事本文（HTML形式）
        slug: 記事のスラッグ（オプション）
        featured_media_id: サムネイル画像ID（オプション）
        status: 記事ステータス（publish, draft, pending等）
        comment_status: コメントステータス（open, closed）
    
    Returns:
        WordPress記事ID（投稿成功時）、None（失敗時）
    """
    config = get_wordpress_config(user_id)
    if not config:
        raise ValueError("WordPress設定が完了していません。設定ページでWordPress情報を登録してください。")
    
    # WordPress REST API URL
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/posts"
    
    # Basic認証ヘッダー
    credentials = f"{config['username']}:{config['app_password']}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    
    # 記事データを準備
    post_data = {
        "title": title,
        "content": content,
        "status": status,
        "comment_status": comment_status,
    }
    
    if slug:
        post_data["slug"] = slug
    
    if featured_media_id:
        post_data["featured_media"] = featured_media_id
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=post_data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("id"):
                return result["id"]
            return None
    except httpx.HTTPStatusError as e:
        error_detail = ""
        if e.response.status_code == 404:
            error_detail = (
                f"WordPress REST APIエンドポイントが見つかりません (404)。\n"
                f"確認事項:\n"
                f"1. WordPressサイトURLが正しいか確認してください（例: https://example.com）\n"
                f"2. WordPress.comのサイトを使用している場合、通常のWordPress REST APIは利用できません。\n"
                f"   自己ホスト型のWordPressサイト（WordPress.org）を使用してください。\n"
                f"3. REST APIが有効になっているか確認してください。\n"
                f"   試しにブラウザで {api_url} にアクセスして確認してください。\n"
                f"4. アプリケーションパスワードが正しいか確認してください。\n"
                f"\nエラー詳細: {e.response.text[:500]}"
            )
        else:
            error_detail = f"WordPress API エラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_detail)
    except httpx.RequestError as e:
        raise Exception(f"WordPress API リクエストエラー: {str(e)}")
    except Exception as e:
        raise Exception(f"WordPress投稿エラー: {str(e)}")

