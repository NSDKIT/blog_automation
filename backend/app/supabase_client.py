"""
Supabaseクライアント
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client | None:
    """Supabaseクライアントを取得（設定されていない場合はNoneを返す）"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        # Supabaseが設定されていない場合はNoneを返す（後で設定可能）
        return None
    
    return create_client(supabase_url, supabase_key)

