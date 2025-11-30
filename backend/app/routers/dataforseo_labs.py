"""
DataForSEO Labs API ルーター
提供されたDataForSEOLabsAPI.pyのコードをベースに実装
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, Optional, List
import requests
import json
import os
from app.dependencies import get_current_user
from app.dataforseo_client import get_dataforseo_config, _get_auth_header
from app.rate_limit import rate_limit

router = APIRouter()

BASE_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google"


@router.post(
    "/analyze",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def analyze_dataforseo_labs(
    request: Request,
    endpoint: str,
    keyword: Optional[str] = None,
    target: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    target1: Optional[str] = None,
    target2: Optional[str] = None,
    targets: Optional[List[str]] = None,
    category_codes: Optional[List[int]] = None,
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    current_user: dict = Depends(get_current_user)
):
    """
    DataForSEO Labs APIを呼び出して結果を返す
    提供されたDataForSEOLabsAPI.pyのコードをベースに実装
    
    Args:
        endpoint: APIエンドポイント名（例: "related_keywords", "keywords_for_site"）
        keyword: キーワード（単一）
        target: ターゲットサイト（単一）
        keywords: キーワードリスト
        target1, target2: ドメイン比較用
        targets: ターゲットサイトリスト
        category_codes: カテゴリーコードリスト
        location_code: 地域コード
        language_code: 言語コード
    """
    user_id = str(current_user.get("id"))
    
    # DataForSEO認証情報を取得
    config = get_dataforseo_config(user_id)
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DataForSEO設定が完了していません。設定ページでDataForSEO情報を登録してください。"
            )
        config = {"login": login, "password": password}
    
    # 認証ヘッダーを生成
    auth_header = _get_auth_header(config["login"], config["password"])
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    # エンドポイントごとのペイロードを生成
    payload_dict = {}
    
    if endpoint == "related_keywords":
        if not keyword:
            raise HTTPException(status_code=400, detail="keywordが必要です")
        payload_dict = {
            "keyword": keyword,
            "location_code": location_code,
            "depth": 3,
            "include_seed_keyword": False,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "replace_with_core_keyword": False,
            "limit": 100
        }
        url = f"{BASE_URL}/related_keywords/live"
    
    elif endpoint == "keywords_for_site":
        if not target:
            raise HTTPException(status_code=400, detail="targetが必要です")
        payload_dict = {
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": False,
            "include_subdomains": True,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100
        }
        url = f"{BASE_URL}/keywords_for_site/live"
    
    elif endpoint == "keyword_suggestions":
        if not keyword:
            raise HTTPException(status_code=400, detail="keywordが必要です")
        payload_dict = {
            "keyword": keyword,
            "location_code": location_code,
            "include_seed_keyword": False,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "exact_match": False,
            "limit": 100
        }
        url = f"{BASE_URL}/keyword_suggestions/live"
    
    elif endpoint == "keyword_ideas":
        if not keywords:
            raise HTTPException(status_code=400, detail="keywordsが必要です")
        payload_dict = {
            "keywords": keywords,
            "location_code": location_code,
            "include_serp_info": False,
            "closely_variants": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100
        }
        url = f"{BASE_URL}/keyword_ideas/live"
    
    elif endpoint == "ranked_keywords":
        if not target:
            raise HTTPException(status_code=400, detail="targetが必要です")
        payload_dict = {
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "historical_serp_mode": "live",
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "load_rank_absolute": False,
            "limit": 100
        }
        url = f"{BASE_URL}/ranked_keywords/live"
    
    elif endpoint == "serp_competitors":
        if not keywords:
            raise HTTPException(status_code=400, detail="keywordsが必要です")
        payload_dict = {
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code,
            "include_subdomains": True,
            "limit": 100
        }
        url = f"{BASE_URL}/serp_competitors/live"
    
    elif endpoint == "competitors_domain":
        if not target:
            raise HTTPException(status_code=400, detail="targetが必要です")
        payload_dict = {
            "target": target,
            "location_code": location_code,
            "language_code": language_code,
            "exclude_top_domains": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100
        }
        url = f"{BASE_URL}/competitors_domain/live"
    
    elif endpoint == "domain_intersection":
        if not target1 or not target2:
            raise HTTPException(status_code=400, detail="target1とtarget2が必要です")
        payload_dict = {
            "target1": target1,
            "target2": target2,
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": False,
            "include_clickstream_data": False,
            "intersections": True,
            "limit": 100
        }
        url = f"{BASE_URL}/domain_intersection/live"
    
    elif endpoint == "keyword_overview":
        if not keywords:
            raise HTTPException(status_code=400, detail="keywordsが必要です")
        payload_dict = {
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": False,
            "include_clickstream_data": False
        }
        url = f"{BASE_URL}/keyword_overview/live"
    
    elif endpoint == "bulk_keyword_difficulty":
        if not keywords:
            raise HTTPException(status_code=400, detail="keywordsが必要です")
        payload_dict = {
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code
        }
        url = f"{BASE_URL}/bulk_keyword_difficulty/live"
    
    elif endpoint == "search_intent":
        if not keywords:
            raise HTTPException(status_code=400, detail="keywordsが必要です")
        payload_dict = {
            "keywords": keywords,
            "language_code": language_code
        }
        url = f"{BASE_URL}/search_intent/live"
    
    elif endpoint == "top_searches":
        payload_dict = {
            "location_code": location_code,
            "language_code": language_code,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100
        }
        url = f"{BASE_URL}/top_searches/live"
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"サポートされていないエンドポイント: {endpoint}"
        )
    
    # ペイロードをJSON文字列に変換
    payload = json.dumps([payload_dict], ensure_ascii=False)
    
    try:
        print(f"[dataforseo_labs] API呼び出し: {endpoint} - {url}")
        print(f"[dataforseo_labs] Payload: {payload}")
        
        response = requests.post(url, headers=headers, data=payload, timeout=120)
        print(f"[dataforseo_labs] レスポンス HTTP Status: {response.status_code}")
        
        # 提供されたDataForSEOLabsAPI.pyと同じ形式で結果を保存
        result = {
            "url": url,
            "payload": payload,
            "headers": dict(headers),
            "response_text": response.text,
            "http_status_code": response.status_code,
        }
        
        # JSONレスポンスをパース（可能な場合）
        try:
            response_json = response.json()
            result["response_json"] = response_json
            
            # エラーステータスコードをチェック
            if isinstance(response_json, dict):
                tasks = response_json.get("tasks", [])
                if tasks and len(tasks) > 0:
                    task_status = tasks[0].get("status_code")
                    task_message = tasks[0].get("status_message", "")
                    if task_status and task_status != 20000:
                        print(f"[dataforseo_labs] APIエラー: status_code={task_status}, message={task_message}")
        except:
            pass
        
        return result
            
    except Exception as e:
        print(f"[dataforseo_labs] API呼び出しエラー: {endpoint} - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"API呼び出しエラー: {str(e)}"
        )

