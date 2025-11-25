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
    """ユーザーのWordPress設定を取得（WordPress.comのみ対応）"""
    site_url = get_setting_by_key(user_id, "wordpress_site_url")
    username = get_setting_by_key(user_id, "wordpress_username")
    api_token = get_setting_by_key(user_id, "wordpress_api_token")
    
    if not site_url or not username or not api_token:
        return None
    
    return {
        "site_url": site_url,
        "username": username,
        "api_token": api_token
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
    WordPress.comに画像をアップロード
    
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
    
    # WordPress.com API v1.1
    # サイトIDは完全なドメイン名（例: example.wordpress.com）
    site_domain = config['site_url'].replace("https://", "").replace("http://", "").strip()
    api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_domain}/media/new"
    
    # WordPress.com APIはBasic認証を使用（ユーザー名:APIトークン）
    credentials = f"{config['username']}:{config['api_token']}"
    auth_base64_bytes = base64.b64encode(credentials.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
    }
    # WordPress.com APIはmultipart/form-dataを使用
    files = {
        'media[]': (image_filename, image_data, mime_type)
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # WordPress.com APIはmultipart/form-dataを使用
            response = await client.post(
                api_url,
                files=files,
                headers=headers
            )
            # WordPress.com APIのレスポンス形式を処理
            result = _check_response(response, 200)  # WordPress.comは200を返す
            # WordPress.com APIのレスポンス形式: {"media": [{"ID": 123, ...}]}
            if result.get("media") and len(result["media"]) > 0:
                return result["media"][0].get("ID")
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
    WordPress.comに記事を投稿
    
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
    
    # WordPress.com API v1.1
    # サイトIDは完全なドメイン名（例: example.wordpress.com）
    site_domain = config['site_url'].replace("https://", "").replace("http://", "").strip()
    api_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site_domain}/posts/new"
    
    # WordPress.com APIはBasic認証を使用（ユーザー名:APIトークン）
    credentials = f"{config['username']}:{config['api_token']}"
    auth_base64_bytes = base64.b64encode(credentials.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/json'
    }
    
    # WordPress.com APIの形式に合わせる
    wp_com_data = {
        'title': title,
        'content': content,
        'status': status,
        'comment_status': comment_status,
    }
    if slug:
        wp_com_data['slug'] = slug
    if featured_media_id:
        wp_com_data['featured_image'] = featured_media_id
    if category_ids:
        wp_com_data['categories'] = category_ids
    if tag_ids:
        wp_com_data['tags'] = tag_ids
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=wp_com_data, headers=headers)
            # WordPress.com APIのレスポンス形式を処理
            result = _check_response(response, 200)  # WordPress.comは200を返す
            # WordPress.com APIのレスポンス形式: {"ID": 123, ...}
            if result.get("ID"):
                return result["ID"]
            return None
    except WordPressError:
        raise
    except httpx.RequestError as e:
        raise WordPressError(0, "Request Error", f"WordPress API リクエストエラー: {str(e)}")
    except Exception as e:
        raise WordPressError(0, "Unknown Error", f"WordPress投稿エラー: {str(e)}")

