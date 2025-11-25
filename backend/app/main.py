from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, articles, settings
from app.config import settings

# データベーステーブルはSupabaseで管理（SQLスクリプトで作成済み）

app = FastAPI(
    title="メガネ記事案ジェネレーター API",
    description="メガネ関連記事を自動生成するAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])
app.include_router(articles.router, prefix="/api/articles", tags=["記事"])
app.include_router(settings.router, prefix="/api/settings", tags=["設定"])


@app.get("/")
async def root():
    return {"message": "メガネ記事案ジェネレーター API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

