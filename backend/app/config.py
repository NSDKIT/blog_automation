"""
アプリケーション設定
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (不要だが互換性のため残す)
    database_url: str = ""
    
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # JWT
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    
    # Anthropic
    anthropic_api_key: str = ""
    
    # Google
    google_api_key: str = ""
    google_cse_id: str = ""
    
    # Gemini
    gemini_api_key: str = ""
    
    # Shopify
    shopify_shop_domain: str = ""
    shopify_access_token: str = ""
    shopify_blog_id: str = ""
    
    # DataForSEO
    dataforseo_login: str = ""
    dataforseo_password: str = ""
    
    # CORS (文字列として受け取り、後でsplit)
    # 環境変数CORS_ORIGINSまたはCORS_ORIGINS_STRから読み込む
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173,https://blog-automation-nu.vercel.app"
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS originsをリストとして返す"""
        # 環境変数から読み込む（優先）
        env_origins = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ORIGINS_STR", "")
        if env_origins:
            origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
        else:
            # デフォルト値を使用
            origins = [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
        return origins
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

