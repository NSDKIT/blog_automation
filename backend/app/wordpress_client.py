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
    # リダイレクトエラーの場合、JSON解析を試みる前にエラーを返す
    if response.status_code == 301 or response.status_code == 302:
        location = response.headers.get('Location', '不明')
        raise WordPressError(
            response.status_code,
            response.reason_phrase or "Redirect",
            (
                f"リダイレクトエラー: WordPress.comのサイトURLが正しくない可能性があります。\n"
                f"確認事項:\n"
                f"1. サイトURLが正しいか確認してください（例: https://example.wordpress.com）\n"
                f"2. URLに末尾のスラッシュ（/）が含まれていないか確認してください\n"
                f"3. WordPress.comのサイトが存在するか確認してください\n"
                f"4. リダイレクト先: {location}\n"
                f"5. WordPress.comでは `/wp-json/wp/v2/` エンドポイントが使えない可能性があります"
            )
        )
    
    try:
        json_object = response.json()
    except (ValueError, json.JSONDecodeError) as ex:
        # JSON解析に失敗した場合、レスポンスの内容を確認
        content_preview = response.text[:200] if response.text else "空のレスポンス"
        raise WordPressError(
            response.status_code,
            response.reason_phrase or "Unknown",
            (
                f"JSON解析エラー: {str(ex)}\n"
                f"レスポンスの内容（最初の200文字）: {content_preview}\n"
                f"これは、WordPress.comのサイトURLが正しくないか、"
                f"`/wp-json/wp/v2/` エンドポイントが使用できない可能性があります。"
            )
        )
    
    # 200と201の両方を成功として扱う（WordPress REST API v2は場合によって200を返す）
    if response.status_code not in [200, 201] and response.status_code != success_code:
        # JSON解析に失敗した場合（HTMLレスポンスなど）の処理
        if isinstance(json_object, dict):
            error_message = json_object.get('message', response.text[:500])
        else:
            # HTMLレスポンスの場合、最初の500文字を表示
            error_message = response.text[:500]
            if response.status_code == 301 or response.status_code == 302:
                error_message = (
                    f"リダイレクトエラー ({response.status_code}): WordPress.comのサイトURLが正しくない可能性があります。\n"
                    f"確認事項:\n"
                    f"1. サイトURLが正しいか確認してください（例: https://example.wordpress.com）\n"
                    f"2. URLに末尾のスラッシュ（/）が含まれていないか確認してください\n"
                    f"3. WordPress.comのサイトが存在するか確認してください\n"
                    f"4. リダイレクト先: {response.headers.get('Location', '不明')}"
                )
        
        # 403エラーの場合、より詳細なメッセージを追加
        if response.status_code == 403:
            error_message += (
                "\n\n認証エラーの可能性があります。以下を確認してください:\n"
                "1. WordPress.comのユーザー名（メールアドレス）が正しいか確認してください\n"
                "2. アプリケーションパスワードが正しく発行されているか確認してください\n"
                "3. アプリケーションパスワードにスペースが含まれている場合は、そのまま入力してください\n"
                "4. WordPress.comのセキュリティ設定（https://wordpress.com/me/security）でアプリケーションパスワードが有効か確認してください\n"
                "5. 2段階認証が有効になっているか確認してください（アプリケーションパスワードを表示するには2段階認証が必要です）"
            )
        
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
    
    # WordPress REST API v2エンドポイントを使用（提供されたコードの方式に従う）
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/media"
    
    # Basic認証（提供されたコードの方式に従う）
    auth_str = f"{config['username']}:{config['api_token']}"
    auth_base64_bytes = base64.b64encode(auth_str.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    # ヘッダー設定（提供されたコードの方式に従う）
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': mime_type,
        'Content-Disposition': f'attachiment; filename={image_filename}'  # 提供コードのtypoに合わせる
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # 画像データを直接送信（提供されたコードの方式に従う）
            response = await client.post(
                api_url,
                content=image_data,
                headers=headers
            )
            
            # レスポンスをチェック（200 OKまたは201 Createdが成功）
            # WordPress REST API v2は場合によって200を返すこともある
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get("id"):
                    return result["id"]
            else:
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
    
    # WordPress REST API v2エンドポイントを使用（提供されたコードの方式に従う）
    api_url = f"{config['site_url'].rstrip('/')}/wp-json/wp/v2/posts"
    
    # Basic認証（提供されたコードの方式に従う）
    auth_str = f"{config['username']}:{config['api_token']}"
    auth_base64_bytes = base64.b64encode(auth_str.encode(encoding='utf-8'))
    auth_base64 = auth_base64_bytes.decode(encoding='utf-8')
    
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/json'
    }
    
    # 記事データを準備（提供されたコードの方式に従う）
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
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.post(api_url, json=post_data, headers=headers)
            
            # レスポンスをチェック（200 OKまたは201 Createdが成功）
            # WordPress REST API v2は場合によって200を返すこともある
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    # レスポンスが配列の場合（WordPress REST API v2の一部のエンドポイント）
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    if result.get("id"):
                        return result["id"]
                except (ValueError, json.JSONDecodeError):
                    # JSON解析に失敗した場合、エラーメッセージを返す
                    raise WordPressError(
                        response.status_code,
                        response.reason_phrase or "Unknown",
                        f"JSON解析エラー: レスポンスがJSON形式ではありません。レスポンス: {response.text[:200]}"
                    )
            else:
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

