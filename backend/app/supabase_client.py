"""
Supabaseクライアント
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client | None:
    """Supabaseクライアントを取得。サービスロールキー優先。"""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url:
        return None

    # サーバー側では RLS を回避するため service role key を優先的に利用
    supabase_key = service_key or anon_key
    if not supabase_key:
        return None

    return create_client(supabase_url, supabase_key)

