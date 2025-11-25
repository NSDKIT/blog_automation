from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Herokuなどの本番環境ではDATABASE_URLが提供される
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/article_generator")

# Herokuでは接続プールを無効化
if "postgres://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 本番環境ではNullPoolを使用（Heroku推奨）
if os.getenv("ENVIRONMENT") == "production":
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

