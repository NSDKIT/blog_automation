from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# 認証スキーマ
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str

    class Config:
        from_attributes = True


# 記事スキーマ
class ArticleCreate(BaseModel):
    keyword: str
    target: str
    article_type: str
    used_type1: Optional[str] = None
    used_type2: Optional[str] = None
    used_type3: Optional[str] = None
    prompt: Optional[str] = None
    important_keyword1: Optional[str] = None
    important_keyword2: Optional[str] = None
    important_keyword3: Optional[str] = None
    sheet_id: str


class ArticleResponse(BaseModel):
    id: UUID
    keyword: str
    target: str
    article_type: str
    title: Optional[str]
    content: Optional[str]
    error_message: Optional[str] = None
    shopify_article_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


# 設定スキーマ
class SettingUpdate(BaseModel):
    key: str
    value: str


class SettingResponse(BaseModel):
    id: UUID
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

