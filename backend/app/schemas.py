from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
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
    sheet_id: Optional[str] = None  # 後方互換性のため残すが、使用しない
    # SEO関連フィールド
    search_intent: Optional[str] = "情報収集"  # 情報収集/購買検討/比較検討/問題解決
    target_location: Optional[str] = "Japan"  # 検索地域
    device_type: Optional[str] = "mobile"  # mobile/desktop
    secondary_keywords: Optional[List[str]] = None  # サブキーワード配列


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
    # SEO関連フィールド
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    search_intent: Optional[str] = None
    target_location: Optional[str] = None
    device_type: Optional[str] = None
    serp_data: Optional[Dict] = None
    serp_headings_analysis: Optional[Dict] = None
    serp_common_patterns: Optional[Dict] = None
    serp_faq_items: Optional[List[str]] = None
    keyword_volume_data: Optional[Dict] = None
    related_keywords: Optional[List[Dict]] = None
    keyword_difficulty: Optional[Dict] = None
    subtopics: Optional[List[str]] = None
    content_structure: Optional[Dict] = None
    structured_data: Optional[Dict] = None
    best_keywords: Optional[List[Dict]] = None  # 最適なキーワードリスト（スコアリング済み）
    analyzed_keywords: Optional[List[Dict]] = None  # 分析済みキーワードリスト（全100個）
    selected_keywords: Optional[List[str]] = None  # ユーザーが選択したキーワード
    selected_keywords_data: Optional[List[Dict]] = None  # 選択されたキーワードの詳細データ
    keyword_analysis_progress: Optional[Dict] = None  # キーワード分析の進捗状況

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
    is_masked: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ユーザー画像スキーマ
class UserImageCreate(BaseModel):
    keyword: str
    image_url: str
    alt_text: Optional[str] = None


class UserImageUpdate(BaseModel):
    keyword: Optional[str] = None
    image_url: Optional[str] = None
    alt_text: Optional[str] = None


class UserImageResponse(BaseModel):
    id: UUID
    keyword: str
    image_url: str
    alt_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ユーザー選択肢スキーマ
class UserOptionCreate(BaseModel):
    category: str  # 'target', 'article_type', 'used_type', 'important_keyword'
    value: str
    display_order: Optional[int] = 0


class UserOptionUpdate(BaseModel):
    value: Optional[str] = None
    display_order: Optional[int] = None


class UserOptionResponse(BaseModel):
    id: UUID
    category: str
    value: str
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
