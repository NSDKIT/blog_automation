"""
DataForSEO SERP Analysis API ルーター
提供されたSERPAPI.pyのコードをベースに実装
SEO対策向けの分析機能を追加
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, Optional, List
import requests
import json
import os
import re
from collections import Counter
from app.dependencies import get_current_user
from app.dataforseo_client import get_dataforseo_config, _get_auth_header
from app.rate_limit import rate_limit

router = APIRouter()


def extract_serp_data(response_json: Dict) -> Optional[Dict]:
    """APIレスポンスからSERPデータを抽出"""
    if not isinstance(response_json, dict):
        return None
    
    tasks = response_json.get("tasks", [])
    if not tasks or len(tasks) == 0:
        return None
    
    task = tasks[0]
    if task.get("status_code") != 20000:
        return None
    
    results = task.get("result", [])
    if not results or len(results) == 0:
        return None
    
    return results[0]


def analyze_headings_structure(serp_data: Dict) -> Dict:
    """見出し構造パターンを分析"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    organic_items = [item for item in items if item.get("type") == "organic"]
    
    # タイトルから見出しパターンを抽出
    h1_patterns = []
    h2_patterns = []
    h3_patterns = []
    title_lengths = []
    
    for item in organic_items[:20]:  # 上位20件を分析
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        
        # タイトル長を記録
        title_lengths.append(len(title))
        
        # 見出しパターンを抽出
        if "とは" in title or "意味" in title or "定義" in title:
            h1_patterns.append("定義・説明型")
        if "選び方" in title or "方法" in title or "やり方" in title:
            h2_patterns.append("選び方・方法型")
        if "おすすめ" in title or "ランキング" in title or "ベスト" in title:
            h2_patterns.append("おすすめ・ランキング型")
        if "比較" in title or "違い" in title:
            h2_patterns.append("比較型")
        if "特徴" in title or "メリット" in title or "デメリット" in title:
            h2_patterns.append("特徴・メリット型")
        if "価格" in title or "値段" in title or "コスト" in title:
            h3_patterns.append("価格・コスト型")
        if "口コミ" in title or "レビュー" in title or "評判" in title:
            h3_patterns.append("口コミ・レビュー型")
    
    # パターンの頻度を集計
    h1_counter = Counter(h1_patterns)
    h2_counter = Counter(h2_patterns)
    h3_counter = Counter(h3_patterns)
    
    # 平均タイトル長を計算
    avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
    
    return {
        "h1_patterns": dict(h1_counter.most_common(5)),
        "h2_patterns": dict(h2_counter.most_common(10)),
        "h3_patterns": dict(h3_counter.most_common(10)),
        "avg_title_length": round(avg_title_length, 1),
        "min_title_length": min(title_lengths) if title_lengths else 0,
        "max_title_length": max(title_lengths) if title_lengths else 0,
        "recommended_title_length": {
            "min": max(15, int(avg_title_length * 0.8)),
            "max": min(60, int(avg_title_length * 1.2))
        }
    }


def analyze_titles(serp_data: Dict) -> Dict:
    """タイトルを分析して最適化提案を生成"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    organic_items = [item for item in items if item.get("type") == "organic"]
    
    titles = [item.get("title", "") for item in organic_items[:10]]  # 上位10件
    
    # タイトルに含まれるキーワードパターンを分析
    keyword_patterns = []
    emotion_words = []
    action_words = []
    
    for title in titles:
        # キーワードの位置を分析
        if len(title) > 0:
            keyword_patterns.append({
                "title": title,
                "length": len(title),
                "has_number": bool(re.search(r'\d+', title)),
                "has_question": "?" in title or "？" in title
            })
        
        # 感情語・行動喚起語を抽出
        if "おすすめ" in title or "人気" in title or "最高" in title:
            emotion_words.append("おすすめ・人気")
        if "徹底" in title or "完全" in title or "究極" in title:
            emotion_words.append("徹底・完全")
        if "選び方" in title or "方法" in title:
            action_words.append("選び方・方法")
        if "比較" in title or "検討" in title:
            action_words.append("比較・検討")
    
    emotion_counter = Counter(emotion_words)
    action_counter = Counter(action_words)
    
    # タイトル案を生成
    title_suggestions = []
    if titles:
        # パターン1: キーワード + おすすめ
        title_suggestions.append({
            "pattern": "キーワード + おすすめ",
            "example": f"{titles[0].split()[0] if titles else 'キーワード'}のおすすめ10選【2025年最新版】",
            "score": 85
        })
        # パターン2: キーワード + 選び方
        title_suggestions.append({
            "pattern": "キーワード + 選び方",
            "example": f"{titles[0].split()[0] if titles else 'キーワード'}の選び方【完全ガイド】",
            "score": 80
        })
        # パターン3: キーワード + 比較
        title_suggestions.append({
            "pattern": "キーワード + 比較",
            "example": f"{titles[0].split()[0] if titles else 'キーワード'}を徹底比較【2025年】",
            "score": 75
        })
    
    return {
        "titles": titles[:10],
        "keyword_patterns": keyword_patterns[:10],
        "emotion_words": dict(emotion_counter.most_common(5)),
        "action_words": dict(action_counter.most_common(5)),
        "title_suggestions": title_suggestions
    }


def extract_faq_items(serp_data: Dict) -> List[Dict]:
    """People Also Ask (PAA)からFAQを抽出"""
    if not serp_data:
        return []
    
    items = serp_data.get("items", [])
    faq_items = []
    
    # People Also Askを抽出
    for item in items:
        if item.get("type") == "people_also_ask":
            questions = item.get("items", [])
            for q in questions:
                question = q.get("question", "")
                answer = q.get("answer", "")
                if question:
                    faq_items.append({
                        "question": question,
                        "answer": answer,
                        "type": "people_also_ask"
                    })
    
    # Related SearchesもFAQ候補として追加
    for item in items:
        if item.get("type") == "related_searches":
            searches = item.get("items", [])
            for s in searches[:5]:  # 上位5件
                query = s.get("text", "")
                if query and "?" in query:
                    faq_items.append({
                        "question": query.replace("?", "").strip(),
                        "answer": "",
                        "type": "related_search"
                    })
    
    return faq_items[:10]  # 最大10件


def analyze_serp_for_seo(serp_data: Dict) -> Dict:
    """SERPデータをSEO対策向けに分析"""
    if not serp_data:
        return {}
    
    headings_analysis = analyze_headings_structure(serp_data)
    titles_analysis = analyze_titles(serp_data)
    faq_items = extract_faq_items(serp_data)
    
    return {
        "headings_analysis": headings_analysis,
        "titles_analysis": titles_analysis,
        "faq_items": faq_items
    }


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
    
    # Google Desktop (Windows) のみを分析（主要な結果として使用）
    primary_request = {
        "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        "payload": [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": "desktop",
            "os": "windows",
            "depth": 100,
            "calculate_rectangles": True,
            "include_serp_info": True
        }]
    }
    
    results = []
    seo_analysis = None
    
    # 主要なリクエストを実行
    try:
        url = primary_request["url"]
        payload = json.dumps(primary_request["payload"], ensure_ascii=False)
        
        response = requests.post(url, headers=headers, data=payload, timeout=120)
        
        result = {
            "url": url,
            "payload": payload,
            "headers": dict(headers),
            "response_text": response.text,
            "http_status_code": response.status_code,
        }
        
        # JSONレスポンスをパース
        try:
            response_json = response.json()
            result["response_json"] = response_json
            
            # SERPデータを抽出してSEO分析
            serp_data = extract_serp_data(response_json)
            if serp_data:
                seo_analysis = analyze_serp_for_seo(serp_data)
            
        except:
            pass
        
        results.append(result)
            
    except Exception as e:
        results.append({
            "url": primary_request["url"],
            "payload": json.dumps(primary_request["payload"], ensure_ascii=False),
            "error": str(e),
            "http_status_code": None,
            "response_text": None,
            "response_json": None
        })
    
    return {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "results": results,
        "seo_analysis": seo_analysis
    }
