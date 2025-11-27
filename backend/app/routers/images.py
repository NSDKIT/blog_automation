from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File, Form
from typing import List, Optional
from uuid import UUID
import os
import uuid
from app.supabase_db import (
    get_user_images_by_user_id, get_user_images_by_keyword,
    get_user_image_by_id, create_user_image, update_user_image, delete_user_image,
    create_audit_log
)
from app.schemas import UserImageCreate, UserImageUpdate, UserImageResponse
from app.dependencies import get_current_user
from app.supabase_client import get_supabase_client
from app.rate_limit import rate_limit
from app.utils import get_client_ip

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


@router.post(
    "",
    response_model=UserImageResponse,
    dependencies=[Depends(rate_limit(limit=20, window_seconds=60))]
)
async def create_user_image_endpoint(
    image_data: UserImageCreate = None,
    keyword: str = Form(None),
    image_url: str = Form(None),
    alt_text: Optional[str] = Form(None),
    file: UploadFile = File(None),
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """新規画像を登録（URLまたはファイルアップロード）"""
    user_id = str(current_user.get("id"))
    
    # ファイルアップロードの場合
    if file:
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="キーワードは必須です"
            )
        
        # Supabase Storageにアップロード
        supabase = get_supabase_client()
        if not supabase:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabaseが設定されていません"
            )
        
        # ファイルを読み込み
        file_content = await file.read()
        file_ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_name = f"{user_id}/{uuid.uuid4()}{file_ext}"
        
        # Storageにアップロード（バケット名: user-images）
        try:
            storage_response = supabase.storage.from_("user-images").upload(
                file_name,
                file_content,
                file_options={"content-type": file.content_type or "image/jpeg"}
            )
            
            # 公開URLを取得
            public_url = supabase.storage.from_("user-images").get_public_url(file_name)
            # get_public_urlは文字列を返す
            if isinstance(public_url, dict):
                image_url = public_url.get("publicUrl", str(public_url))
            else:
                image_url = str(public_url)
        except Exception as e:
            error_msg = str(e)
            if "Bucket not found" in error_msg or "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="画像ストレージバケットが設定されていません。Supabaseで'user-images'バケットを作成してください。"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"画像のアップロードに失敗しました: {error_msg}"
            )
    
    # URL指定の場合
    elif image_data:
        keyword = image_data.keyword
        image_url = image_data.image_url
        alt_text = image_data.alt_text
    elif image_url and keyword:
        # Formデータの場合
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像URLまたはファイルのいずれかが必要です"
        )
    
    if not keyword or not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="キーワードと画像URLは必須です"
        )
    
    image = create_user_image(
        user_id=user_id,
        keyword=keyword,
        image_url=image_url,
        alt_text=alt_text
    )
    create_audit_log(
        user_id=user_id,
        action="image_created",
        metadata={"image_id": image.get("id"), "keyword": keyword},
        ip_address=get_client_ip(request)
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


@router.put(
    "/{image_id}",
    response_model=UserImageResponse,
    dependencies=[Depends(rate_limit(limit=30, window_seconds=60))]
)
async def update_user_image_endpoint(
    image_id: UUID,
    image_update: UserImageUpdate,
    request: Request,
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
    
    create_audit_log(
        user_id=user_id,
        action="image_updated",
        metadata={"image_id": str(image_id), "fields": list(updates.keys())},
        ip_address=get_client_ip(request)
    )
    return image


@router.delete(
    "/{image_id}",
    dependencies=[Depends(rate_limit(limit=30, window_seconds=60))]
)
async def delete_user_image_endpoint(
    image_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """画像を削除（Storageからも削除）"""
    user_id = str(current_user.get("id"))
    
    # 既存の画像を確認
    existing_image = get_user_image_by_id(str(image_id), user_id)
    if not existing_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="画像が見つかりません"
        )
    
    # Supabase Storageから削除（URLがStorageのパスを含む場合）
    image_url = existing_image.get("image_url", "")
    if "storage" in image_url and user_id in image_url:
        try:
            supabase = get_supabase_client()
            if supabase:
                # URLからファイルパスを抽出
                # 例: https://xxx.supabase.co/storage/v1/object/public/user-images/user_id/file.jpg
                path_parts = image_url.split("/user-images/")
                if len(path_parts) > 1:
                    file_path = path_parts[1]
                    supabase.storage.from_("user-images").remove([file_path])
        except Exception as e:
            # Storage削除の失敗はログに記録するが、DB削除は続行
            print(f"Storage削除エラー（無視）: {e}")
    
    # データベースから削除
    delete_user_image(str(image_id), user_id)
    create_audit_log(
        user_id=user_id,
        action="image_deleted",
        metadata={"image_id": str(image_id)},
        ip_address=get_client_ip(request)
    )
    
    return {"message": "画像を削除しました"}
