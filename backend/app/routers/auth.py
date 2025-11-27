from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.supabase_db import get_user_by_email, create_user, create_audit_log
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user
from app.rate_limit import rate_limit
from app.utils import get_client_ip

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    dependencies=[Depends(rate_limit(limit=5, window_seconds=60))]
)
async def register(user_data: UserRegister, request: Request):
    # 既存ユーザーチェック
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )
    
    # 新規ユーザー作成
    hashed_password = get_password_hash(user_data.password)
    new_user = create_user(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
        role="user"
    )

    create_audit_log(
        user_id=str(new_user.get("id")),
        action="user_registered",
        metadata={"email": user_data.email},
        ip_address=get_client_ip(request)
    )
    
    return new_user


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def login(user_data: UserLogin, request: Request):
    user = get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user.get("password_hash")):
        create_audit_log(
            user_id=None if not user else str(user.get("id")),
            action="user_login_failed",
            metadata={"email": user_data.email},
            ip_address=get_client_ip(request)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.get("id"))})
    create_audit_log(
        user_id=str(user.get("id")),
        action="user_login_success",
        metadata={"email": user_data.email},
        ip_address=get_client_ip(request)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user
