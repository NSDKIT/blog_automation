from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.supabase_db import (
    get_user_options_by_category, get_user_option_by_id,
    create_user_option, update_user_option, delete_user_option
)
from app.schemas import UserOptionCreate, UserOptionUpdate, UserOptionResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[UserOptionResponse])
async def get_user_options(
    category: str,
    current_user: dict = Depends(get_current_user)
):
    """ユーザーの選択肢一覧を取得（カテゴリ指定）"""
    user_id = str(current_user.get("id"))
    
    if category not in ['target', 'article_type', 'used_type', 'important_keyword']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なカテゴリです。'target', 'article_type', 'used_type', 'important_keyword' のいずれかを指定してください。"
        )
    
    options = get_user_options_by_category(user_id, category)
    return options


@router.post("", response_model=UserOptionResponse)
async def create_user_option_endpoint(
    option_data: UserOptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """新規選択肢を登録"""
    user_id = str(current_user.get("id"))
    
    if option_data.category not in ['target', 'article_type', 'used_type', 'important_keyword']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なカテゴリです。'target', 'article_type', 'used_type', 'important_keyword' のいずれかを指定してください。"
        )
    
    option = create_user_option(
        user_id=user_id,
        category=option_data.category,
        value=option_data.value,
        display_order=option_data.display_order or 0
    )
    
    return option


@router.get("/{option_id}", response_model=UserOptionResponse)
async def get_user_option(
    option_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """選択肢を取得"""
    user_id = str(current_user.get("id"))
    option = get_user_option_by_id(str(option_id), user_id)
    
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="選択肢が見つかりません"
        )
    
    return option


@router.put("/{option_id}", response_model=UserOptionResponse)
async def update_user_option_endpoint(
    option_id: UUID,
    option_update: UserOptionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """選択肢を更新"""
    user_id = str(current_user.get("id"))
    
    # 既存の選択肢を確認
    existing_option = get_user_option_by_id(str(option_id), user_id)
    if not existing_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="選択肢が見つかりません"
        )
    
    # 更新内容を準備
    updates = {}
    if option_update.value is not None:
        updates["value"] = option_update.value
    if option_update.display_order is not None:
        updates["display_order"] = option_update.display_order
    
    # 選択肢を更新
    option = update_user_option(str(option_id), user_id, updates)
    
    if not option:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="選択肢の更新に失敗しました"
        )
    
    return option


@router.delete("/{option_id}")
async def delete_user_option_endpoint(
    option_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """選択肢を削除"""
    user_id = str(current_user.get("id"))
    
    # 既存の選択肢を確認
    existing_option = get_user_option_by_id(str(option_id), user_id)
    if not existing_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="選択肢が見つかりません"
        )
    
    # 選択肢を削除
    delete_user_option(str(option_id), user_id)
    
    return {"message": "選択肢を削除しました"}

