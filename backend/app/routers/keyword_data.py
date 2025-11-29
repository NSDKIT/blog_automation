"""
DataForSEO Keyword Data API ルーター
提供されたKeywordDataAPI.pyのコードをベースに実装
SEO対策向けの分析機能を追加
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, Optional, List
import requests
import json
import base64
import os
from app.dependencies import get_current_user
from app.dataforseo_client import get_dataforseo_config, _get_auth_header
from app.rate_limit import rate_limit

router = APIRouter()


def extract_keyword_data(response_json: Dict) -> Optional[Dict]:
    """APIレスポンスからキーワードデータを抽出"""
    if not isinstance(response_json, dict):
        return None
    
    tasks = response_json.get("tasks", [])
    if not tasks or len(tasks) == 0:
        return None
    
    task = tasks[0]
    if task.get("status_code") != 20000:
        return None
    
    result = task.get("result", [])
    if not result or len(result) == 0:
        return None
    
    return result[0]


def calculate_keyword_score(keyword_data: Dict) -> Dict:
    """キーワードスコアを計算"""
    search_volume = keyword_data.get("search_volume", 0)
    competition_index = keyword_data.get("competition_index", 100)
    cpc = keyword_data.get("cpc", 0)
    
    # 検索ボリュームスコア (0-100)
    volume_score = min(100, (search_volume / 100000) * 100) if search_volume > 0 else 0
    
    # 競合度スコア (0-100, 低競合ほど高スコア)
    competition_score = max(0, 100 - competition_index)
    
    # CPC効率スコア (0-100, CPCが低いほど高スコア)
    cpc_score = max(0, 100 - (cpc * 10)) if cpc > 0 else 50
    
    # 総合スコア
    total_score = (
        volume_score * 0.4 +
        competition_score * 0.3 +
        cpc_score * 0.2 +
        50 * 0.1  # トレンドスコア（後で実装可能）
    )
    
    return {
        "volume_score": round(volume_score, 1),
        "competition_score": round(competition_score, 1),
        "cpc_score": round(cpc_score, 1),
        "total_score": round(total_score, 1)
    }


def calculate_roi_metrics(keyword_data: Dict) -> Dict:
    """ROI計算"""
    search_volume = keyword_data.get("search_volume", 0)
    cpc = keyword_data.get("cpc", 0)
    
    # 月間推定クリック数（検索ボリュームの1%がクリックと仮定）
    monthly_clicks = int(search_volume * 0.01)
    
    # 月間広告費試算
    monthly_ad_cost = monthly_clicks * cpc
    
    # 年間広告費試算
    yearly_ad_cost = monthly_ad_cost * 12
    
    # 推定獲得トラフィック（SEOの場合、検索ボリュームの5%を獲得と仮定）
    monthly_seo_traffic = int(search_volume * 0.05)
    
    return {
        "monthly_clicks": monthly_clicks,
        "monthly_ad_cost": round(monthly_ad_cost, 2),
        "yearly_ad_cost": round(yearly_ad_cost, 2),
        "monthly_seo_traffic": monthly_seo_traffic,
        "cpc": cpc
    }


def check_alerts(keyword_data: Dict, previous_data: Optional[Dict] = None) -> List[Dict]:
    """アラートチェック"""
    alerts = []
    
    search_volume = keyword_data.get("search_volume", 0)
    competition_index = keyword_data.get("competition_index", 100)
    cpc = keyword_data.get("cpc", 0)
    
    # 検索ボリュームが低い場合
    if search_volume < 1000:
        alerts.append({
            "type": "warning",
            "message": f"検索ボリュームが低いです ({search_volume:,})。記事の効果が限定的になる可能性があります。"
        })
    
    # 競合度が高い場合
    if competition_index > 70:
        alerts.append({
            "type": "warning",
            "message": f"競合度が高いです (競合インデックス: {competition_index})。上位表示が困難な可能性があります。"
        })
    
    # CPCが高い場合
    if cpc > 5:
        alerts.append({
            "type": "info",
            "message": f"CPCが高いです (${cpc:.2f})。広告運用時のコストが高くなる可能性があります。"
        })
    
    # 前回データとの比較（実装可能な場合）
    if previous_data:
        prev_volume = previous_data.get("search_volume", 0)
        if prev_volume > 0:
            volume_change = ((search_volume - prev_volume) / prev_volume) * 100
            if abs(volume_change) > 20:
                alerts.append({
                    "type": "info" if volume_change > 0 else "warning",
                    "message": f"検索ボリュームが{volume_change:+.1f}%変化しています。"
                })
    
    return alerts


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
    SEO対策向けの分析機能を追加
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
    
    # リクエストデータを準備
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
    keyword_data = None
    related_keywords = []
    
    # 各APIを呼び出し
    for req in requests_data:
        try:
            response = requests.post(req["url"], headers=headers, data=req["payload"], timeout=120)
            
            results[req["name"]] = {
                "url": req["url"],
                "payload": req["payload"],
                "headers": dict(headers),
                "response_text": response.text,
                "http_status_code": response.status_code,
            }
            
            # JSONレスポンスをパース
            try:
                response_json = response.json()
                results[req["name"]]["response_json"] = response_json
                
                # キーワードデータを抽出
                if req["name"] == "response1":
                    keyword_data = extract_keyword_data(response_json)
                elif req["name"] == "response3":
                    # 関連キーワードを抽出
                    if isinstance(response_json, dict):
                        tasks = response_json.get("tasks", [])
                        if tasks and len(tasks) > 0 and tasks[0].get("status_code") == 20000:
                            related_results = tasks[0].get("result", [])
                            if related_results:
                                related_keywords = related_results[:10]  # 上位10個
                
            except:
                pass
                
        except Exception as e:
            results[req["name"]] = {
                "url": req["url"],
                "payload": req["payload"],
                "error": str(e),
                "http_status_code": None,
                "response_text": None,
                "response_json": None
            }
    
    # SEO分析結果を構築
    seo_analysis = None
    if keyword_data:
        scores = calculate_keyword_score(keyword_data)
        roi_metrics = calculate_roi_metrics(keyword_data)
        alerts = check_alerts(keyword_data)
        
        seo_analysis = {
            "keyword_data": keyword_data,
            "scores": scores,
            "roi_metrics": roi_metrics,
            "alerts": alerts,
            "related_keywords": related_keywords[:5] if related_keywords else []
        }
    
    return {
        "keyword": keyword,
        "location_code": location_code,
        "results": results,
        "seo_analysis": seo_analysis
    }
