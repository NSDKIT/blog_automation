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
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """CORS originsをリストとして返す"""
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

