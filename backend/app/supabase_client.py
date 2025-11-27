"""
Supabaseクライアント
"""
import os
from typing import Optional

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_RLS_MODE = os.getenv("SUPABASE_RLS_MODE", "service").lower()


def _select_key(use_service_role: bool) -> Optional[str]:
    if use_service_role:
        return SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
    if SUPABASE_RLS_MODE in {"enforced", "anon"}:
        return SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY
    return SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY


def get_supabase_client(use_service_role: bool = False) -> Client | None:
    """Supabaseクライアントを取得。環境変数でRLSモードを制御。"""
    if not SUPABASE_URL:
        return None

    supabase_key = _select_key(use_service_role)
    if not supabase_key:
        return None

    return create_client(SUPABASE_URL, supabase_key)


def get_supabase_service_client() -> Client | None:
    """明示的にサービスロールキーを使用するクライアントを取得"""
    return get_supabase_client(use_service_role=True)
