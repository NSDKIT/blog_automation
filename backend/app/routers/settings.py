from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List
from app.supabase_db import get_settings_by_user_id, upsert_setting, create_audit_log
from app.schemas import SettingUpdate, SettingResponse
from app.dependencies import get_current_user
from app.security import EncryptionKeyMissing
from app.rate_limit import rate_limit
from app.utils import get_client_ip

router = APIRouter()


@router.get("", response_model=List[SettingResponse])
async def get_settings(
    current_user: dict = Depends(get_current_user)
):
    settings = get_settings_by_user_id(str(current_user.get("id")))
    return settings


@router.put(
    "",
    response_model=SettingResponse,
    dependencies=[Depends(rate_limit(limit=30, window_seconds=60))]
)
async def update_setting(
    setting_data: SettingUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # 設定を更新または作成
    try:
        setting = upsert_setting(
            user_id=str(current_user.get("id")),
            key=setting_data.key,
            value=setting_data.value
        )
    except EncryptionKeyMissing as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
    create_audit_log(
        user_id=str(current_user.get("id")),
        action="setting_updated",
        metadata={"key": setting_data.key, "is_masked": setting.get("is_masked")},
        ip_address=get_client_ip(request)
    )
    return setting
