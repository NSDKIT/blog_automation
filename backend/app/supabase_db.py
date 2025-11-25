"""
Supabaseクライアントを使用したデータベース操作
全てのデータをSupabaseで管理
"""
from app.supabase_client import get_supabase_client
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid
from postgrest.exceptions import APIError


_article_error_column_supported: Optional[bool] = None


def get_supabase():
    """Supabaseクライアントを取得"""
    client = get_supabase_client()
    if not client:
        raise ValueError("Supabase client is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY.")
    return client


def _supports_article_error_column() -> bool:
    """
    Supabase上にerror_messageカラムが存在するかをキャッシュ付きで判定
    存在しない場合はFalseを返し、以後の更新でerror_messageを除外する
    """
    global _article_error_column_supported
    if _article_error_column_supported is not None:
        return _article_error_column_supported

    supabase = get_supabase()
    try:
        supabase.table("articles").select("error_message").limit(1).execute()
        _article_error_column_supported = True
    except APIError as exc:
        if "error_message" in str(exc):
            _article_error_column_supported = False
        else:
            raise
    return _article_error_column_supported


def _load_latest_article_error(article_id: str) -> Optional[str]:
    """記事履歴から直近のエラーメッセージを取得"""
    supabase = get_supabase()
    response = (
        supabase.table("article_histories")
        .select("changes, created_at")
        .eq("article_id", article_id)
        .eq("action", "failed")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if response.data and len(response.data) > 0:
        changes = response.data[0].get("changes") or {}
        return changes.get("error_message")
    return None


def _attach_error_message(article: Optional[Dict]) -> Optional[Dict]:
    """レスポンスにerror_messageキーを追加（必要なら履歴から補完）"""
    if not article:
        return article

    article.setdefault("error_message", None)
    if article.get("status") == "failed" and not article.get("error_message"):
        try:
            article["error_message"] = _load_latest_article_error(article.get("id"))
        except Exception:
            # 履歴の取得に失敗しても既存処理には影響させない
            pass
    return article


# ============================================
# Users操作
# ============================================

def get_user_by_email(email: str) -> Optional[Dict]:
    """メールアドレスでユーザーを取得"""
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("email", email).limit(1).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """IDでユーザーを取得"""
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def create_user(email: str, password_hash: str, name: str, role: str = "user") -> Dict:
    """新規ユーザーを作成"""
    supabase = get_supabase()
    user_data = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "role": role
    }
    response = supabase.table("users").insert(user_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    raise Exception("Failed to create user")


# ============================================
# Articles操作
# ============================================

def get_articles_by_user_id(user_id: str, skip: int = 0, limit: int = 100) -> List[Dict]:
    """ユーザーIDで記事一覧を取得"""
    supabase = get_supabase()
    response = supabase.table("articles")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()
    articles = response.data or []
    return [_attach_error_message(article) for article in articles]


def get_article_by_id(article_id: str, user_id: str) -> Optional[Dict]:
    """記事IDで記事を取得（ユーザーIDでフィルタ）"""
    supabase = get_supabase()
    response = supabase.table("articles")\
        .select("*")\
        .eq("id", article_id)\
        .eq("user_id", user_id)\
        .limit(1)\
        .execute()
    if response.data and len(response.data) > 0:
        return _attach_error_message(response.data[0])
    return None


def create_article(user_id: str, keyword: str, target: str, article_type: str, status: str = "processing") -> Dict:
    """新規記事を作成"""
    supabase = get_supabase()
    article_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "keyword": keyword,
        "target": target,
        "article_type": article_type,
        "status": status
    }
    response = supabase.table("articles").insert(article_data).execute()
    if response.data and len(response.data) > 0:
        return _attach_error_message(response.data[0])
    raise Exception("Failed to create article")


def update_article(article_id: str, user_id: str, updates: Dict) -> Optional[Dict]:
    """記事を更新"""
    supabase = get_supabase()
    update_payload = dict(updates)
    if "error_message" in update_payload and not _supports_article_error_column():
        update_payload.pop("error_message", None)
    response = supabase.table("articles")\
        .update(update_payload)\
        .eq("id", article_id)\
        .eq("user_id", user_id)\
        .execute()
    if response.data and len(response.data) > 0:
        return _attach_error_message(response.data[0])
    return None


def delete_article(article_id: str, user_id: str) -> bool:
    """記事を削除"""
    supabase = get_supabase()
    response = supabase.table("articles")\
        .delete()\
        .eq("id", article_id)\
        .eq("user_id", user_id)\
        .execute()
    return True


def create_article_history(article_id: str, action: str, changes: Optional[Dict] = None) -> Dict:
    """記事履歴を作成"""
    supabase = get_supabase()
    history_data = {
        "id": str(uuid.uuid4()),
        "article_id": article_id,
        "action": action,
        "changes": changes
    }
    response = supabase.table("article_histories").insert(history_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    raise Exception("Failed to create article history")


# ============================================
# Settings操作
# ============================================

def get_settings_by_user_id(user_id: str) -> List[Dict]:
    """ユーザーIDで設定一覧を取得"""
    supabase = get_supabase()
    response = supabase.table("settings")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    return response.data or []


def get_setting_by_key(user_id: str, key: str) -> Optional[str]:
    """ユーザーIDとキーで設定値を取得"""
    supabase = get_supabase()
    response = supabase.table("settings")\
        .select("value")\
        .eq("user_id", user_id)\
        .eq("key", key)\
        .limit(1)\
        .execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0].get("value")
    return None


def upsert_setting(user_id: str, key: str, value: str) -> Dict:
    """設定を更新または作成"""
    supabase = get_supabase()
    # 既存の設定を確認
    existing = supabase.table("settings")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("key", key)\
        .limit(1)\
        .execute()
    
    setting_data = {
        "user_id": user_id,
        "key": key,
        "value": value
    }
    
    if existing.data and len(existing.data) > 0:
        # 更新
        response = supabase.table("settings")\
            .update(setting_data)\
            .eq("user_id", user_id)\
            .eq("key", key)\
            .execute()
    else:
        # 新規作成
        setting_data["id"] = str(uuid.uuid4())
        response = supabase.table("settings").insert(setting_data).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    raise Exception("Failed to upsert setting")

