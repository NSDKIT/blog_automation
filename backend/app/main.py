from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth as auth_router, articles as articles_router, settings as settings_router, images as images_router, options as options_router
from app.config import settings as app_settings

# データベーステーブルはSupabaseで管理（SQLスクリプトで作成済み）

app = FastAPI(
    title="メガネ記事案ジェネレーター API",
    description="メガネ関連記事を自動生成するAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(auth_router.router, prefix="/api/auth", tags=["認証"])
app.include_router(articles_router.router, prefix="/api/articles", tags=["記事"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["設定"])
app.include_router(images_router.router, prefix="/api/images", tags=["画像"])
app.include_router(options_router.router, prefix="/api/options", tags=["選択肢"])


@app.get("/")
async def root():
    return {"message": "メガネ記事案ジェネレーター API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

