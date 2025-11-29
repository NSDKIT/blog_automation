"""
DataForSEO SERP Analysis API ルーター
提供されたSERPAPI.pyのコードをベースに実装
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
async def analyze_serp(
    request: Request,
    keyword: str,
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    current_user: dict = Depends(get_current_user)
):
    """
    SERPデータを分析（提供されたSERPAPI.pyのコードをベースに実装）
    複数のDataForSEO SERP APIを呼び出して結果をそのまま返す
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
    
    # デバッグ用ログ（認証情報は含めない）
    print(f"[serp_analysis] 認証情報を使用: login={config['login'][:10]}... (認証ヘッダー長: {len(auth_header)})")
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    print(f"[serp_analysis] リクエストヘッダー: {headers}")
    
    # リクエストパターンのリスト（提供されたSERPAPI.pyと同じ形式）
    request_patterns = [
        {
            "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "desktop",
                "os": "windows",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "desktop",
                "os": "macos",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "mobile",
                "os": "android",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "mobile",
                "os": "ios",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "desktop",
                "os": "windows",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "desktop",
                "os": "macos",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "mobile",
                "os": "android",
                "depth": 100
            }]
        },
        {
            "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
            "payload": [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": "mobile",
                "os": "ios",
                "depth": 100
            }]
        },
    ]
    
    # レスポンスデータリスト（提供されたSERPAPI.pyと同じ形式）
    results = []
    
    # 各リクエストパターンを実行
    for pattern in request_patterns:
        try:
            url = pattern["url"]
            payload = json.dumps(pattern["payload"], ensure_ascii=False)
            
            print(f"[serp_analysis] API呼び出し: {url}")
            print(f"[serp_analysis] Payload: {payload}")
            
            response = requests.post(url, headers=headers, data=payload, timeout=120)
            print(f"[serp_analysis] レスポンス HTTP Status: {response.status_code}")
            
            # 提供されたSERPAPI.pyと同じ形式で結果を保存
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
                            print(f"[serp_analysis] APIエラー: status_code={task_status}, message={task_message}")
            except:
                pass
            
            results.append(result)
                
        except Exception as e:
            print(f"[serp_analysis] API呼び出しエラー: {url} - {str(e)}")
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
        "location_code": location_code,
        "language_code": language_code,
        "results": results
    }

