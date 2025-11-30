"""
統合分析API ルーター
tougou.mdの仕様に基づいて、複数のDataForSEO APIを統合して包括的なキーワード分析を提供
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


def get_competition_level(competition_index: int) -> str:
    """競合度インデックスから競合レベルを判定"""
    if competition_index < 30:
        return "LOW"
    elif competition_index < 70:
        return "MED"
    else:
        return "HIGH"


def get_difficulty_level(keyword_difficulty: int) -> str:
    """難易度から判定を返す"""
    if keyword_difficulty <= 30:
        return "即攻略"
    elif keyword_difficulty <= 50:
        return "中期目標"
    else:
        return "長期目標"


def calculate_commercial_value_coefficient(cpc: float) -> float:
    """CPCから商業価値係数を計算"""
    if cpc < 0.30:
        return 1.0
    elif cpc <= 1.00:
        return 1.2
    else:
        return 1.5


def calculate_priority_score(
    search_volume: int,
    cpc: float,
    keyword_difficulty: int
) -> float:
    """
    優先度スコアを計算
    score = (検索ボリューム × 商業価値係数) ÷ (難易度 + 10)
    """
    commercial_coefficient = calculate_commercial_value_coefficient(cpc)
    score = (search_volume * commercial_coefficient) / (keyword_difficulty + 10)
    return round(score, 2)


def estimate_recommended_rank(keyword_difficulty: int) -> int:
    """
    推奨順位を推定（難易度が低いほど上位表示の可能性が高い）
    簡易的な推定: 難易度0-30 → 3-10位、31-50 → 10-20位、51-100 → 20-30位
    """
    if keyword_difficulty <= 30:
        return 3 + (keyword_difficulty // 5)  # 3-9位
    elif keyword_difficulty <= 50:
        return 10 + ((keyword_difficulty - 30) // 2)  # 10-20位
    else:
        return 20 + ((keyword_difficulty - 50) // 2)  # 20-30位


@router.post(
    "/analyze",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def integrated_analysis(
    request: Request,
    keyword: str,
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    current_user: dict = Depends(get_current_user)
):
    """
    統合分析エンドポイント
    メインキーワードと関連キーワードの包括的な分析を実行
    """
    config = get_dataforseo_config(current_user.get("id")) if current_user.get("id") else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DataForSEO設定が完了していません。"
            )
        config = {"login": login, "password": password}
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    # 1. メインキーワードの分析
    main_keyword_data = None
    try:
        # Google Ads Search Volume APIでメインキーワードのデータを取得
        # KeywordDataAPI.pyと同じ形式（language_codeは使用しない）
        url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
        payload = [{
            "keywords": [keyword],
            "sort_by": "relevance"
        }]
        
        # DomainAnalyticsAPI.pyと同じ形式で送信（json.dumpsを使用）
        payload_json = json.dumps(payload, ensure_ascii=False)
        
        # DomainAnalyticsと同じくrequests.postを使用
        response = requests.post(url, headers=headers, data=payload_json, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                if task.get("status_code") == 20000:
                    task_result = task.get("result", [])
                    if task_result and len(task_result) > 0:
                        main_keyword_data = task_result[0]
    except Exception as e:
        error_msg = f"メインキーワード分析エラー: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        # メインキーワードのエラーは致命的ではないので、続行
    
    # 2. 関連キーワードの取得（DataForSEO Labs related_keywords API）
    related_keywords_data = []
    try:
        url = f"{BASE_URL}/related_keywords/live"
        # DomainAnalyticsAPI.pyと同じ形式（language_nameは使用しない）
        payload = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "depth": 3,
            "include_seed_keyword": False,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "replace_with_core_keyword": False,
            "limit": 100  # DomainAnalyticsAPI.pyと同じ固定値
        }]
        
        # DomainAnalyticsAPI.pyと同じ形式で送信（json.dumpsを使用）
        payload_json = json.dumps(payload, ensure_ascii=False)
        
        # DomainAnalyticsと同じくrequests.postを使用
        response = requests.post(url, headers=headers, data=payload_json, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        # DataForSEO APIのエラーステータスをチェック
        if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                status_message = task.get("status_message", "")
                
                if status_code != 20000:
                    error_detail = f"DataForSEO API エラー (status_code: {status_code}): {status_message}"
                    if status_code == 40200:
                        error_detail = "DataForSEO APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか確認してください。"
                    elif status_code == 40100:
                        error_detail = "DataForSEO APIの認証に失敗しました。認証情報を確認してください。"
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_detail
                    )
                
                task_result = task.get("result", [])
                if task_result and len(task_result) > 0:
                    related_keywords_raw = task_result[0].get("items", [])
                    
                    # 各関連キーワードの詳細データを取得
                    related_keywords_list = [item.get("keyword", "") for item in related_keywords_raw[:100]]  # 最大100件
                    
                    # bulk_keyword_difficulty APIで難易度を一括取得
                    if related_keywords_list:
                        difficulty_url = f"{BASE_URL}/bulk_keyword_difficulty/live"
                        # DomainAnalyticsAPI.pyと同じ形式（language_nameは使用しない）
                        difficulty_payload = [{
                            "keywords": related_keywords_list,
                            "location_code": location_code,
                            "language_code": language_code
                        }]
                        
                        # DomainAnalyticsと同じくrequests.postを使用
                        difficulty_payload_json = json.dumps(difficulty_payload, ensure_ascii=False)
                        difficulty_response = requests.post(
                            difficulty_url, headers=headers, data=difficulty_payload_json, timeout=120
                        )
                        difficulty_response.raise_for_status()
                        difficulty_result = difficulty_response.json()
                        
                        difficulty_map = {}
                        if difficulty_result.get("tasks") and len(difficulty_result["tasks"]) > 0:
                                difficulty_task = difficulty_result["tasks"][0]
                                difficulty_status_code = difficulty_task.get("status_code")
                                if difficulty_status_code == 20000:
                                    difficulty_items = difficulty_task.get("result", [])
                                    if difficulty_items and len(difficulty_items) > 0:
                                        for item in difficulty_items[0].get("items", []):
                                            kw = item.get("keyword", "")
                                            difficulty_map[kw] = item.get("keyword_difficulty", 50)
                                else:
                                    # 難易度取得のエラーは致命的ではないので、デフォルト値を使用
                                    print(f"難易度取得エラー (status_code: {difficulty_status_code}): {difficulty_task.get('status_message', '')}")
                    
                    # 各関連キーワードの検索ボリュームとCPCを取得
                    # KeywordDataAPI.pyと同じ形式（language_codeは使用しない）
                    search_volume_url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
                    search_volume_payload = [{
                        "keywords": related_keywords_list,
                        "sort_by": "relevance"
                    }]
                    
                    # DomainAnalyticsと同じくrequests.postを使用
                    sv_payload_json = json.dumps(search_volume_payload, ensure_ascii=False)
                    sv_response = requests.post(
                        search_volume_url, headers=headers, data=sv_payload_json, timeout=120
                    )
                    sv_response.raise_for_status()
                    sv_result = sv_response.json()
                    
                    sv_map = {}
                    if sv_result.get("tasks") and len(sv_result["tasks"]) > 0:
                            sv_task = sv_result["tasks"][0]
                            sv_status_code = sv_task.get("status_code")
                            if sv_status_code == 20000:
                                sv_items = sv_task.get("result", [])
                                for item in sv_items:
                                    kw = item.get("keyword", "")
                                    sv_map[kw] = {
                                        "search_volume": item.get("search_volume", 0),
                                        "cpc": item.get("cpc", 0),
                                        "competition_index": item.get("competition_index", 50)
                                    }
                            else:
                                # 検索ボリューム取得のエラーは致命的ではないので、デフォルト値を使用
                                print(f"検索ボリューム取得エラー (status_code: {sv_status_code}): {sv_task.get('status_message', '')}")
                    
                    # データを統合
                    for item in related_keywords_raw[:100]:  # 最大100件
                        kw = item.get("keyword", "")
                        if not kw:
                            continue
                        
                        sv_data = sv_map.get(kw, {})
                        search_volume = sv_data.get("search_volume", 0)
                        cpc = sv_data.get("cpc", 0)
                        competition_index = sv_data.get("competition_index", 50)
                        keyword_difficulty = difficulty_map.get(kw, 50)
                        
                        competition_level = get_competition_level(competition_index)
                        difficulty_level = get_difficulty_level(keyword_difficulty)
                        priority_score = calculate_priority_score(search_volume, cpc, keyword_difficulty)
                        recommended_rank = estimate_recommended_rank(keyword_difficulty)
                        
                        related_keywords_data.append({
                            "keyword": kw,
                            "search_volume": search_volume,
                            "cpc": round(cpc, 2),
                            "competition": competition_level,
                            "competition_index": competition_index,
                            "difficulty": keyword_difficulty,
                            "difficulty_level": difficulty_level,
                            "priority_score": priority_score,
                            "recommended_rank": recommended_rank
                        })
    except HTTPException:
        # HTTPExceptionはそのまま再スロー
        raise
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTPエラー: {e.response.status_code if e.response else 'Unknown'} - {e.response.text[:500] if e.response else str(e)}"
        print(f"関連キーワード分析エラー: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"関連キーワード分析中にHTTPエラーが発生しました: {error_msg}"
        )
    except requests.exceptions.RequestException as e:
        error_msg = f"リクエストエラー: {str(e)}"
        print(f"関連キーワード分析エラー: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"関連キーワード分析中にリクエストエラーが発生しました: {error_msg}"
        )
    except Exception as e:
        error_msg = f"関連キーワード分析エラー: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"関連キーワード分析中にエラーが発生しました: {str(e)}"
        )
    
    # 関連キーワードを優先度スコア順にソート
    related_keywords_data.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # メインキーワードの分析結果を整形
    main_keyword_result = None
    if main_keyword_data:
        search_volume = main_keyword_data.get("search_volume", 0)
        cpc = main_keyword_data.get("cpc", 0)
        competition_index = main_keyword_data.get("competition_index", 50)
        
        # メインキーワードの難易度を取得
        main_difficulty = 50  # デフォルト値
        try:
            difficulty_url = f"{BASE_URL}/bulk_keyword_difficulty/live"
            # DomainAnalyticsAPI.pyと同じ形式（language_nameは使用しない）
            difficulty_payload = [{
                "keywords": [keyword],
                "location_code": location_code,
                "language_code": language_code
            }]
            
            # DomainAnalyticsと同じくrequests.postを使用
            difficulty_payload_json = json.dumps(difficulty_payload, ensure_ascii=False)
            difficulty_response = requests.post(
                difficulty_url, headers=headers, data=difficulty_payload_json, timeout=120
            )
            difficulty_response.raise_for_status()
            difficulty_result = difficulty_response.json()
            
            if difficulty_result.get("tasks") and len(difficulty_result["tasks"]) > 0:
                    difficulty_task = difficulty_result["tasks"][0]
                    if difficulty_task.get("status_code") == 20000:
                        difficulty_items = difficulty_task.get("result", [])
                        if difficulty_items and len(difficulty_items) > 0:
                            items = difficulty_items[0].get("items", [])
                            if items and len(items) > 0:
                                main_difficulty = items[0].get("keyword_difficulty", 50)
        except Exception as e:
            error_msg = f"メインキーワード難易度取得エラー: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            # 難易度取得のエラーは致命的ではないので、デフォルト値を使用
        
        competition_level = get_competition_level(competition_index)
        difficulty_level = get_difficulty_level(main_difficulty)
        
        main_keyword_result = {
            "keyword": keyword,
            "search_volume": search_volume,
            "cpc": round(cpc, 2),
            "competition": competition_level,
            "competition_index": competition_index,
            "difficulty": main_difficulty,
            "difficulty_level": difficulty_level
        }
    
    # サマリー統計を計算
    summary_stats = {
        "immediate_attack": {
            "count": len([kw for kw in related_keywords_data if kw["difficulty_level"] == "即攻略"]),
            "total_volume": sum([kw["search_volume"] for kw in related_keywords_data if kw["difficulty_level"] == "即攻略"])
        },
        "medium_term": {
            "count": len([kw for kw in related_keywords_data if kw["difficulty_level"] == "中期目標"]),
            "total_volume": sum([kw["search_volume"] for kw in related_keywords_data if kw["difficulty_level"] == "中期目標"])
        },
        "long_term": {
            "count": len([kw for kw in related_keywords_data if kw["difficulty_level"] == "長期目標"]),
            "total_volume": sum([kw["search_volume"] for kw in related_keywords_data if kw["difficulty_level"] == "長期目標"])
        }
    }
    
    # AI推奨戦略を生成
    immediate_keywords = [kw for kw in related_keywords_data if kw["difficulty_level"] == "即攻略"][:10]
    recommended_strategy = {
        "phase1": {
            "keywords": immediate_keywords,
            "estimated_traffic": sum([kw["search_volume"] for kw in immediate_keywords]) * 0.03,  # CTR 3%想定
            "period": "1-2ヶ月"
        }
    }
    
    return {
        "main_keyword": main_keyword_result,
        "related_keywords": related_keywords_data,
        "summary_stats": summary_stats,
        "recommended_strategy": recommended_strategy,
        "total_count": len(related_keywords_data)
    }

