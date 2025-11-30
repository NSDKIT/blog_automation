from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi import Request
from app.routers import auth as auth_router, articles as articles_router, settings as settings_router, images as images_router, options as options_router, keyword_data as keyword_data_router, serp_analysis as serp_analysis_router, domain_analytics as domain_analytics_router, dataforseo_labs as dataforseo_labs_router, integrated_analysis as integrated_analysis_router, integrated_analysis_results as integrated_analysis_results_router
from app.config import settings as app_settings
import os

# データベーステーブルはSupabaseで管理（SQLスクリプトで作成済み）

app = FastAPI(
    title="メガネ記事案ジェネレーター API",
    description="メガネ関連記事を自動生成するAPI",
    version="1.0.0"
)

# CORS設定
cors_origins = app_settings.cors_origins
# 環境変数から直接読み込む（フォールバック）
if not cors_origins or len(cors_origins) == 0:
    env_origins = os.getenv("CORS_ORIGINS", "https://blog-automation-nu.vercel.app,http://localhost:3000,http://localhost:5173")
    cors_origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]

print(f"[CORS] Allowed origins: {cors_origins}")  # デバッグ用

# CORSミドルウェアを追加（ルーター登録の前が重要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# OPTIONSリクエストを明示的に処理（念のため）
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """OPTIONSリクエストを明示的に処理"""
    origin = request.headers.get("origin")
    if origin in cors_origins:
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    return Response(status_code=200)

# ルーターを登録
app.include_router(auth_router.router, prefix="/api/auth", tags=["認証"])
app.include_router(articles_router.router, prefix="/api/articles", tags=["記事"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["設定"])
app.include_router(images_router.router, prefix="/api/images", tags=["画像"])
app.include_router(options_router.router, prefix="/api/options", tags=["選択肢"])
app.include_router(keyword_data_router.router, prefix="/api/keyword-data", tags=["キーワードデータ"])
app.include_router(serp_analysis_router.router, prefix="/api/serp-analysis", tags=["SERP分析"])
app.include_router(domain_analytics_router.router, prefix="/api/domain-analytics", tags=["Domain Analytics"])
app.include_router(dataforseo_labs_router.router, prefix="/api/dataforseo-labs", tags=["DataForSEO Labs"])
app.include_router(integrated_analysis_router.router, prefix="/api/integrated-analysis", tags=["統合分析"])
app.include_router(integrated_analysis_results_router.router, prefix="/api/integrated-analysis-results", tags=["統合分析結果"])


@app.get("/")
async def root():
    return {"message": "メガネ記事案ジェネレーター API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

