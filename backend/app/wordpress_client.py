"""
WordPress REST API クライアント
ユーザーごとのWordPress設定を使用して記事を投稿
Application PasswordプラグインまたはWordPress 5.6以降の標準機能を使用
"""
import httpx
import base64
import mimetypes
import json
from typing import Dict, Optional
from app.supabase_db import get_setting_by_key


class WordPressError(Exception):
    """WordPressのエラー情報"""
    def __init__(self, status_code: int, reason: str, message: str):
        super(WordPressError, self).__init__()
        self.status_code = status_code
        self.reason = reason
        self.message = message
    
    def __str__(self):
        return f"WordPress Error [{self.status_code} {self.reason}]: {self.message}"


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


def _check_response(response: httpx.Response, success_code: int) -> Dict:
    """
    WordPressからの応答をチェック
    
    Args:
        response: HTTPレスポンス
        success_code: 成功時のHTTPステータスコード
    
    Returns:
        JSONレスポンスデータ
    
    Raises:
        WordPressError: エラーが発生した場合
    """
    try:
        json_object = response.json()
    except (ValueError, json.JSONDecodeError) as ex:
        raise WordPressError(
            response.status_code,
            response.reason_phrase or "Unknown",
            f"JSON解析エラー: {str(ex)}"
        )
    
    if response.status_code != success_code:
        error_message = json_object.get('message', response.text[:500]) if isinstance(json_object, dict) else response.text[:500]
        raise WordPressError(
            response.status_code,
            response.reason_phrase or "Unknown",
            error_message
        )
    
    return json_object


async def upload_image_to_wordpress(
    user_id: str,
    image_url: str,
    image_filename: str = "image.jpg"
) -> Optional[int]:
    """
    WordPressに画像をアップロード
    Application PasswordプラグインまたはWordPress 5.6以降の標準機能を使用
    
    Args:
        user_id: ユーザーID
        image_url: 画像のURL
        image_filename: 画像ファイル名
    
    Returns:
        画像ID（アップロード成功時）、None（失敗時）
    
    Raises:
        ValueError: WordPress設定が未完了の場合
        WordPressError: WordPress APIエラーの場合
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
        raise WordPressError(0, "Download Error", f"画像のダウンロードに失敗しました: {str(e)}")
    
    # MIMEタイプを取得
    mime_type, _ = mimetypes.guess_type(image_filename)
    if not mime_type:
        # 拡張子から推測できない場合はデフォルトでJPEG
        if image_filename.lower().endswith('.png'):
            mime_type = "image/png"
        elif image_filename.lower().endswith('.gif'):
            mime_type = "image/gif"
        else:
            mime_type = "image/jpeg"
    
    # WordPress REST API URL
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/media"
    
    # Basic認証ヘッダー（Application Password方式）
    credentials = f"{config['username']}:{config['app_password']}"
    auth_base64_bytes = base64.b64encode(credentials.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    # ヘッダー設定（提供されたコードの方式に合わせる）
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': mime_type,
        'Content-Disposition': f'attachment; filename={image_filename}'
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                content=image_data,
                headers=headers
            )
            
            # レスポンスをチェック（201 Createdが成功）
            result = _check_response(response, 201)
            
            if result.get("id"):
                return result["id"]
            return None
    except WordPressError:
        raise
    except httpx.RequestError as e:
        raise WordPressError(0, "Request Error", f"WordPress API リクエストエラー: {str(e)}")
    except Exception as e:
        raise WordPressError(0, "Unknown Error", f"WordPress画像アップロードエラー: {str(e)}")


async def publish_article_to_wordpress(
    user_id: str,
    title: str,
    content: str,
    slug: Optional[str] = None,
    featured_media_id: Optional[int] = None,
    status: str = "publish",
    comment_status: str = "closed",
    category_ids: Optional[list] = None,
    tag_ids: Optional[list] = None
) -> Optional[int]:
    """
    WordPressに記事を投稿
    Application PasswordプラグインまたはWordPress 5.6以降の標準機能を使用
    
    Args:
        user_id: ユーザーID
        title: 記事タイトル
        content: 記事本文（HTML形式）
        slug: 記事のスラッグ（オプション）
        featured_media_id: サムネイル画像ID（オプション）
        status: 記事ステータス（publish, draft, pending等）
        comment_status: コメントステータス（open, closed）
        category_ids: カテゴリIDのリスト（オプション）
        tag_ids: タグIDのリスト（オプション）
    
    Returns:
        WordPress記事ID（投稿成功時）、None（失敗時）
    
    Raises:
        ValueError: WordPress設定が未完了の場合
        WordPressError: WordPress APIエラーの場合
    """
    config = get_wordpress_config(user_id)
    if not config:
        raise ValueError("WordPress設定が完了していません。設定ページでWordPress情報を登録してください。")
    
    # WordPress REST API URL
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/posts"
    
    # Basic認証ヘッダー（Application Password方式）
    credentials = f"{config['username']}:{config['app_password']}"
    auth_base64_bytes = base64.b64encode(credentials.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/json'
    }
    
    # 記事データを準備（提供されたコードの方式に合わせる）
    post_data = {
        'title': title,
        'content': content,
        'format': 'standard',
        'status': status,
        'comment_status': comment_status,
    }
    
    if slug:
        post_data['slug'] = slug
    
    if featured_media_id:
        post_data['featured_media'] = featured_media_id
    
    if category_ids:
        post_data['categories'] = category_ids
    
    if tag_ids:
        post_data['tags'] = tag_ids
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=post_data, headers=headers)
            
            # レスポンスをチェック（201 Createdが成功）
            result = _check_response(response, 201)
            
            if result.get("id"):
                return result["id"]
            return None
    except WordPressError:
        raise
    except httpx.RequestError as e:
        raise WordPressError(0, "Request Error", f"WordPress API リクエストエラー: {str(e)}")
    except Exception as e:
        raise WordPressError(0, "Unknown Error", f"WordPress投稿エラー: {str(e)}")

