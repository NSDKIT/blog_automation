from fastapi import APIRouter, Depends, HTTPException, status
from app.supabase_db import get_user_by_email, create_user
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
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
    
    return new_user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.get("id"))})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

