from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.supabase_db import get_settings_by_user_id, upsert_setting
from app.schemas import SettingUpdate, SettingResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[SettingResponse])
async def get_settings(
    current_user: dict = Depends(get_current_user)
):
    settings = get_settings_by_user_id(str(current_user.get("id")))
    return settings


@router.put("", response_model=SettingResponse)
async def update_setting(
    setting_data: SettingUpdate,
    current_user: dict = Depends(get_current_user)
):
    # 設定を更新または作成
    setting = upsert_setting(
        user_id=str(current_user.get("id")),
        key=setting_data.key,
        value=setting_data.value  # 実際には暗号化が必要
    )
    
    return setting

