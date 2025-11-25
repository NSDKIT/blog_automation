from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.supabase_db import (
    get_user_images_by_user_id, get_user_images_by_keyword,
    get_user_image_by_id, create_user_image, update_user_image, delete_user_image
)
from app.schemas import UserImageCreate, UserImageUpdate, UserImageResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[UserImageResponse])
async def get_user_images(
    keyword: str = None,
    current_user: dict = Depends(get_current_user)
):
    """ユーザーの画像一覧を取得"""
    user_id = str(current_user.get("id"))
    
    if keyword:
        images = get_user_images_by_keyword(user_id, keyword)
    else:
        images = get_user_images_by_user_id(user_id)
    
    return images


@router.post("", response_model=UserImageResponse)
async def create_user_image_endpoint(
    image_data: UserImageCreate,
    current_user: dict = Depends(get_current_user)
):
    """新規画像を登録"""
    user_id = str(current_user.get("id"))
    
    image = create_user_image(
        user_id=user_id,
        keyword=image_data.keyword,
        image_url=image_data.image_url,
        alt_text=image_data.alt_text
    )
    
    return image


@router.get("/{image_id}", response_model=UserImageResponse)
async def get_user_image(
    image_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """画像を取得"""
    user_id = str(current_user.get("id"))
    image = get_user_image_by_id(str(image_id), user_id)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="画像が見つかりません"
        )
    
    return image


@router.put("/{image_id}", response_model=UserImageResponse)
async def update_user_image_endpoint(
    image_id: UUID,
    image_update: UserImageUpdate,
    current_user: dict = Depends(get_current_user)
):
    """画像を更新"""
    user_id = str(current_user.get("id"))
    
    # 既存の画像を確認
    existing_image = get_user_image_by_id(str(image_id), user_id)
    if not existing_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="画像が見つかりません"
        )
    
    # 更新内容を準備
    updates = {}
    if image_update.keyword is not None:
        updates["keyword"] = image_update.keyword
    if image_update.image_url is not None:
        updates["image_url"] = image_update.image_url
    if image_update.alt_text is not None:
        updates["alt_text"] = image_update.alt_text
    
    # 画像を更新
    image = update_user_image(str(image_id), user_id, updates)
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像の更新に失敗しました"
        )
    
    return image


@router.delete("/{image_id}")
async def delete_user_image_endpoint(
    image_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """画像を削除"""
    user_id = str(current_user.get("id"))
    
    # 既存の画像を確認
    existing_image = get_user_image_by_id(str(image_id), user_id)
    if not existing_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="画像が見つかりません"
        )
    
    # 画像を削除
    delete_user_image(str(image_id), user_id)
    
    return {"message": "画像を削除しました"}

