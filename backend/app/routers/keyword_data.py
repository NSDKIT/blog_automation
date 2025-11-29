"""
DataForSEO Keyword Data API ルーター
提供されたKeywordDataAPI.pyのコードをベースに実装
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, Optional
import requests
import json
import base64
import os
from app.dependencies import get_current_user
from app.dataforseo_client import get_dataforseo_config, _get_auth_header
from app.rate_limit import rate_limit

router = APIRouter()


@router.post(
    "/analyze",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def analyze_keyword_data(
    request: Request,
    keyword: str,
    location_code: int = 2840,  # 日本
    current_user: dict = Depends(get_current_user)
):
    """
    キーワードデータを分析（提供されたKeywordDataAPI.pyのコードをベースに実装）
    複数のDataForSEO APIを呼び出して結果をそのまま返す
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
    print(f"[keyword_data] 認証情報を使用: login={config['login'][:10]}... (認証ヘッダー長: {len(auth_header)})")
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    print(f"[keyword_data] リクエストヘッダー: {headers}")
    
    # リクエストデータを準備（提供されたコードをベースに）
    requests_data = [
        {
            "name": "response1",
            "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
            "payload": json.dumps([{"keywords": [keyword], "sort_by": "relevance"}]),
        },
        {
            "name": "response2",
            "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_site/live",
            "payload": json.dumps([{"target": keyword, "location_code": location_code, "language_code": "ja", "sort_by": "relevance"}]),
        },
        {
            "name": "response3",
            "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live",
            "payload": json.dumps([{"keywords": [keyword], "sort_by": "relevance"}]),
        },
        {
            "name": "response4",
            "url": "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live",
            "payload": json.dumps([{"keywords": [keyword]}]),
        },
        {
            "name": "response5",
            "url": "https://api.dataforseo.com/v3/keywords_data/dataforseo_trends/explore/live",
            "payload": json.dumps([{"keywords": [keyword], "location_code": location_code}]),
        },
    ]
    
    results = {}
    
    # 各APIを呼び出し（提供されたKeywordDataAPI.pyと同じ形式で）
    for req in requests_data:
        try:
            print(f"[keyword_data] API呼び出し: {req['name']} - {req['url']}")
            print(f"[keyword_data] Payload: {req['payload']}")
            response = requests.post(req["url"], headers=headers, data=req["payload"], timeout=120)
            print(f"[keyword_data] レスポンス HTTP Status: {response.status_code}")
            
            # 提供されたKeywordDataAPI.pyと同じ形式で結果を保存
            results[req["name"]] = {
                "url": req["url"],
                "payload": req["payload"],
                "headers": dict(headers),  # 提供されたコードと同じ形式
                "response_text": response.text,  # 提供されたコードと同じ形式
                "http_status_code": response.status_code,  # HTTPステータスコード（追加情報）
            }
            
            # JSONレスポンスをパース（可能な場合）
            try:
                response_json = response.json()
                results[req["name"]]["response_json"] = response_json
                
                # エラーステータスコードをチェック
                if isinstance(response_json, dict):
                    tasks = response_json.get("tasks", [])
                    if tasks and len(tasks) > 0:
                        task_status = tasks[0].get("status_code")
                        task_message = tasks[0].get("status_message", "")
                        if task_status and task_status != 20000:
                            print(f"[keyword_data] APIエラー: status_code={task_status}, message={task_message}")
            except:
                pass
                
        except Exception as e:
            print(f"[keyword_data] API呼び出しエラー: {req['name']} - {str(e)}")
            results[req["name"]] = {
                "url": req["url"],
                "payload": req["payload"],
                "error": str(e),
                "http_status_code": None,
                "response_text": None,
                "response_json": None
            }
    
    return {
        "keyword": keyword,
        "location_code": location_code,
        "results": results
    }

