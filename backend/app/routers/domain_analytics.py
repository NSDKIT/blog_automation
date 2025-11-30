"""
DataForSEO Domain Analytics API ルーター
提供されたDomainAnalyticsAPI.pyのコードをベースに実装
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


@router.post(
    "/analyze",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def analyze_domain_analytics(
    request: Request,
    keyword: Optional[str] = None,
    target: Optional[str] = None,
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    current_user: dict = Depends(get_current_user)
):
    """
    Domain Analyticsデータを分析（提供されたDomainAnalyticsAPI.pyのコードをベースに実装）
    複数のDataForSEO Labs APIを呼び出して結果をそのまま返す
    
    Args:
        keyword: キーワード（related_keywords, keyword_suggestions, keyword_ideasで使用）
        target: ターゲットサイト（keywords_for_siteで使用）
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
    
    # リクエストパターンのリスト（提供されたDomainAnalyticsAPI.pyと同じ形式）
    request_patterns = []
    
    # related_keywords（キーワードが必要）
    if keyword:
        request_patterns.append({
            "name": "related_keywords",
            "url": "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "depth": 3,
                "include_seed_keyword": False,
                "include_serp_info": False,
                "ignore_synonyms": False,
                "include_clickstream_data": False,
                "replace_with_core_keyword": False,
                "limit": 100,
            }]
        })
        
        # keyword_suggestions（キーワードが必要）
        request_patterns.append({
            "name": "keyword_suggestions",
            "url": "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "include_seed_keyword": False,
                "include_serp_info": False,
                "ignore_synonyms": False,
                "include_clickstream_data": False,
                "exact_match": False,
                "limit": 100,
            }]
        })
        
        # keyword_ideas（キーワードが必要）
        request_patterns.append({
            "name": "keyword_ideas",
            "url": "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live",
            "payload": [{
                "keywords": [keyword],
                "location_code": location_code,
                "include_serp_info": False,
                "closely_variants": False,
                "ignore_synonyms": False,
                "include_clickstream_data": False,
                "limit": 100,
            }]
        })
    
    # keywords_for_site（targetが必要）
    if target:
        request_patterns.append({
            "name": "keywords_for_site",
            "url": "https://api.dataforseo.com/v3/dataforseo_labs/google/keywords_for_site/live",
            "payload": [{
                "target": target,
                "location_code": location_code,
                "language_code": language_code,
                "include_serp_info": False,
                "include_subdomains": True,
                "ignore_synonyms": False,
                "include_clickstream_data": False,
                "limit": 100,
            }]
        })
    
    if not request_patterns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="keywordまたはtargetのいずれかを指定してください"
        )
    
    # レスポンスデータリスト（提供されたDomainAnalyticsAPI.pyと同じ形式）
    results = []
    
    # 各リクエストパターンを実行
    for pattern in request_patterns:
        try:
            url = pattern["url"]
            payload = json.dumps(pattern["payload"], ensure_ascii=False)
            
            print(f"[domain_analytics] API呼び出し: {pattern['name']} - {url}")
            
            response = requests.post(url, headers=headers, data=payload, timeout=120)
            print(f"[domain_analytics] レスポンス HTTP Status: {response.status_code}")
            
            # 提供されたDomainAnalyticsAPI.pyと同じ形式で結果を保存
            result = {
                "url": url,
                "payload": payload,
                "headers": dict(headers),  # 提供されたコードと同じ形式
                "response_text": response.text,  # 提供されたコードと同じ形式
                "http_status_code": response.status_code,  # HTTPステータスコード（追加情報）
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
                            print(f"[domain_analytics] APIエラー: status_code={task_status}, message={task_message}")
            except:
                pass
            
            results.append(result)
                
        except Exception as e:
            print(f"[domain_analytics] API呼び出しエラー: {pattern['name']} - {str(e)}")
            results.append({
                "url": pattern["url"],
                "payload": json.dumps(pattern["payload"], ensure_ascii=False),
                "error": str(e),
                "http_status_code": None,
                "response_text": None,
                "response_json": None
            })
    
    return {
        "keyword": keyword,
        "target": target,
        "location_code": location_code,
        "language_code": language_code,
        "results": results
    }

