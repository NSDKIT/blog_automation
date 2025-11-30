"""
統合分析結果の保存・取得API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from app.dependencies import get_current_user
from app.supabase_db import get_supabase
from app.rate_limit import rate_limit

router = APIRouter()


class IntegratedAnalysisCreate(BaseModel):
    keyword: str
    location_code: int = 2840
    language_code: str = "ja"
    main_keyword: Optional[Dict[str, Any]] = None
    related_keywords: Optional[List[Dict[str, Any]]] = None
    summary_stats: Optional[Dict[str, Any]] = None
    recommended_strategy: Optional[Dict[str, Any]] = None


class IntegratedAnalysisResponse(BaseModel):
    id: UUID
    user_id: UUID
    keyword: str
    location_code: int
    language_code: str
    main_keyword: Optional[Dict[str, Any]] = None
    related_keywords: Optional[List[Dict[str, Any]]] = None
    summary_stats: Optional[Dict[str, Any]] = None
    recommended_strategy: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post(
    "/",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))],
    response_model=IntegratedAnalysisResponse
)
async def create_integrated_analysis(
    data: IntegratedAnalysisCreate,
    current_user: dict = Depends(get_current_user)
):
    """統合分析結果を保存"""
    user_id = str(current_user.get("id"))
    supabase = get_supabase()
    
    try:
        result = supabase.table("integrated_analyses").insert({
            "user_id": user_id,
            "keyword": data.keyword,
            "location_code": data.location_code,
            "language_code": data.language_code,
            "main_keyword": data.main_keyword,
            "related_keywords": data.related_keywords,
            "summary_stats": data.summary_stats,
            "recommended_strategy": data.recommended_strategy
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create integrated analysis"
            )
        
        return IntegratedAnalysisResponse(**result.data[0])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating integrated analysis: {str(e)}"
        )


@router.get(
    "/",
    dependencies=[Depends(rate_limit(limit=30, window_seconds=60))],
    response_model=List[IntegratedAnalysisResponse]
)
async def list_integrated_analyses(
    current_user: dict = Depends(get_current_user)
):
    """ユーザーの統合分析結果一覧を取得"""
    user_id = str(current_user.get("id"))
    supabase = get_supabase()
    
    try:
        result = supabase.table("integrated_analyses")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return [IntegratedAnalysisResponse(**row) for row in result.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching integrated analyses: {str(e)}"
        )


@router.get(
    "/{analysis_id}",
    dependencies=[Depends(rate_limit(limit=30, window_seconds=60))],
    response_model=IntegratedAnalysisResponse
)
async def get_integrated_analysis(
    analysis_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """統合分析結果を取得"""
    user_id = str(current_user.get("id"))
    supabase = get_supabase()
    
    try:
        result = supabase.table("integrated_analyses")\
            .select("*")\
            .eq("id", str(analysis_id))\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integrated analysis not found"
            )
        
        return IntegratedAnalysisResponse(**result.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching integrated analysis: {str(e)}"
        )


@router.delete(
    "/{analysis_id}",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def delete_integrated_analysis(
    analysis_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """統合分析結果を削除"""
    user_id = str(current_user.get("id"))
    supabase = get_supabase()
    
    try:
        result = supabase.table("integrated_analyses")\
            .delete()\
            .eq("id", str(analysis_id))\
            .eq("user_id", user_id)\
            .execute()
        
        return {"message": "Integrated analysis deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting integrated analysis: {str(e)}"
        )

