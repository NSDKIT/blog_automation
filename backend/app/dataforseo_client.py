"""
DataForSEO API クライアント
SEO対策のための各種APIを統合
"""
import os
import base64
import httpx
import json
from typing import Dict, List, Optional, Any
from app.supabase_db import get_setting_by_key


def get_dataforseo_config(user_id: str) -> Optional[Dict[str, str]]:
    """ユーザーのDataForSEO設定を取得"""
    login = get_setting_by_key(user_id, "dataforseo_login")
    password = get_setting_by_key(user_id, "dataforseo_password")
    
    if not login or not password:
        return None
    
    return {
        "login": login,
        "password": password
    }


def _get_auth_header(login: str, password: str) -> str:
    """Basic認証ヘッダーを生成"""
    credentials = f"{login}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


async def get_serp_data(
    keyword: str,
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    device: str = "mobile",
    depth: int = 50,
    user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    SERP API（検索エンジン結果ページAPI）でGoogle検索結果を取得
    
    Args:
        keyword: 検索キーワード
        location_code: 地域コード（2840=日本）
        language_code: 言語コード（ja=日本語）
        device: デバイスタイプ（mobile/desktop）
        depth: 取得する結果数（最大50）
        user_id: ユーザーID（設定から取得する場合）
    
    Returns:
        SERP分析結果の辞書
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        # 環境変数から取得を試みる
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。設定ページでDataForSEO情報を登録してください。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/serp/google/organic/advanced/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    payload = [{
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": device,
        "depth": depth,
        "calculate_rectangles": True,  # 見出し構造を取得
        "include_serp_info": True,  # SERP情報を含める
        "include_subdomains": True
    }]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                
                # エラーステータスコードをチェック
                if status_code == 20000:  # 成功
                    return task.get("result", [{}])[0] if task.get("result") else None
                else:
                    status_message = task.get("status_message", "Unknown error")
                    error_message = f"DataForSEO SERP API エラー (status_code: {status_code}): {status_message}"
                    
                    # Payment Requiredエラーの場合
                    if status_code == 40200:
                        error_message = f"DataForSEO SERP APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか確認してください。"
                    
                    raise Exception(error_message)
            
            # タスクが存在しない場合
            raise Exception("DataForSEO SERP API: レスポンスにタスクが含まれていません")
    except httpx.HTTPStatusError as e:
        error_message = f"DataForSEO SERP API HTTPエラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_message)
    except httpx.RequestError as e:
        error_message = f"DataForSEO SERP API リクエストエラー: {str(e)}"
        raise Exception(error_message)
    except Exception as e:
        # 既にExceptionの場合はそのまま再スロー
        raise


async def get_keywords_data(
    keywords: List[str],
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    user_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Keywords Data APIでキーワードの検索ボリューム、競合度、関連キーワードを取得
    
    Args:
        keywords: キーワードリスト（最大100個）
        location_code: 地域コード（2840=日本）
        language_code: 言語コード（ja=日本語）
        user_id: ユーザーID（設定から取得する場合）
    
    Returns:
        キーワードデータのリスト
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keywords_for_keywords/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    # 最大100キーワードまでバッチ処理
    keywords_batch = keywords[:100]
    
    payload = [{
        "keywords": keywords_batch,
        "location_code": location_code,
        "language_code": language_code,
        "include_serp_info": True,
        "limit": 20  # 各キーワードの関連キーワードを20個取得
    }]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                
                # エラーステータスコードをチェック
                if status_code == 20000:
                    return task.get("result", [])
                else:
                    status_message = task.get("status_message", "Unknown error")
                    error_message = f"DataForSEO Keywords API エラー (status_code: {status_code}): {status_message}"
                    
                    # Payment Requiredエラーの場合
                    if status_code == 40200:
                        error_message = f"DataForSEO Keywords APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか確認してください。"
                    
                    raise Exception(error_message)
            
            # タスクが存在しない場合
            raise Exception("DataForSEO Keywords API: レスポンスにタスクが含まれていません")
    except httpx.HTTPStatusError as e:
        error_message = f"DataForSEO Keywords API HTTPエラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_message)
    except httpx.RequestError as e:
        error_message = f"DataForSEO Keywords API リクエストエラー: {str(e)}"
        raise Exception(error_message)
    except Exception as e:
        # 既にExceptionの場合はそのまま再スロー
        raise


async def get_keywords_data_google_ads(
    keywords: List[str],
    location_code: int = 2840,  # 日本
    language_code: str = "ja",
    user_id: Optional[str] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Google Ads APIベースのKeywords Data APIで検索ボリュームを取得
    より正確なデータを提供（dataforseo_labsよりも高精度）
    
    Args:
        keywords: キーワードリスト（最大100個）
        location_code: 地域コード（2840=日本）
        language_code: 言語コード（ja=日本語）
        user_id: ユーザーID（設定から取得する場合）
    
    Returns:
        キーワードデータのリスト
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    # 最大100キーワードまでバッチ処理
    keywords_batch = keywords[:100]
    
    payload = [{
        "keywords": keywords_batch,
        "location_code": location_code,
        "language_code": language_code,
        "sort_by": "relevance"
    }]
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                
                # エラーステータスコードをチェック
                if status_code == 20000:
                    return task.get("result", [])
                else:
                    status_message = task.get("status_message", "Unknown error")
                    error_message = f"DataForSEO Google Ads API エラー (status_code: {status_code}): {status_message}"
                    
                    # Payment Requiredエラーの場合
                    if status_code == 40200:
                        error_message = f"Google Ads APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか、Google Ads APIへのアクセス権限があるか確認してください。"
                    
                    raise Exception(error_message)
            
            # タスクが存在しない場合
            raise Exception("DataForSEO Google Ads API: レスポンスにタスクが含まれていません")
    except httpx.HTTPStatusError as e:
        error_message = f"DataForSEO Google Ads API HTTPエラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_message)
    except httpx.RequestError as e:
        error_message = f"DataForSEO Google Ads API リクエストエラー: {str(e)}"
        raise Exception(error_message)
    except Exception as e:
        # 既にExceptionの場合はそのまま再スロー
        raise


async def generate_meta_tags(
    title: str,
    content: str,
    user_id: Optional[str] = None
) -> Optional[Dict[str, str]]:
    """
    Content Generation APIでメタタグを生成
    
    Args:
        title: 記事タイトル
        content: 記事本文
        user_id: ユーザーID（設定から取得する場合）
    
    Returns:
        メタタイトルとメタディスクリプションの辞書
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/content_generation/generate_meta_tags/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    payload = [{
        "text": content[:5000],  # 最大5000文字
        "title": title,
        "meta_title_max_length": 60,
        "meta_description_max_length": 160
    }]
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                
                # エラーステータスコードをチェック
                if status_code == 20000:
                    task_result = task.get("result", [{}])[0] if task.get("result") else {}
                    return {
                        "meta_title": task_result.get("meta_title", ""),
                        "meta_description": task_result.get("meta_description", "")
                    }
                else:
                    status_message = task.get("status_message", "Unknown error")
                    error_message = f"DataForSEO Content Generation API エラー (status_code: {status_code}): {status_message}"
                    
                    # Payment Requiredエラーの場合
                    if status_code == 40200:
                        error_message = f"DataForSEO Content Generation APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか確認してください。"
                    
                    raise Exception(error_message)
            
            # タスクが存在しない場合
            raise Exception("DataForSEO Content Generation API: レスポンスにタスクが含まれていません")
    except httpx.HTTPStatusError as e:
        error_message = f"DataForSEO Content Generation API HTTPエラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_message)
    except httpx.RequestError as e:
        error_message = f"DataForSEO Content Generation API リクエストエラー: {str(e)}"
        raise Exception(error_message)
    except Exception as e:
        # 既にExceptionの場合はそのまま再スロー
        raise


async def generate_subtopics(
    keyword: str,
    user_id: Optional[str] = None
) -> Optional[List[str]]:
    """
    Content Generation APIでサブトピックを生成
    
    Args:
        keyword: メインキーワード
        user_id: ユーザーID（設定から取得する場合）
    
    Returns:
        サブトピックのリスト（最大10個）
    """
    config = get_dataforseo_config(user_id) if user_id else None
    
    if not config:
        login = os.getenv("DATAFORSEO_LOGIN")
        password = os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise ValueError("DataForSEO設定が完了していません。")
        config = {"login": login, "password": password}
    
    url = "https://api.dataforseo.com/v3/content_generation/generate_subtopics/live"
    
    headers = {
        "Authorization": _get_auth_header(config["login"], config["password"]),
        "Content-Type": "application/json"
    }
    
    payload = [{
        "keyword": keyword,
        "limit": 10
    }]
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]
                status_code = task.get("status_code")
                
                # エラーステータスコードをチェック
                if status_code == 20000:
                    task_result = task.get("result", [{}])[0] if task.get("result") else {}
                    subtopics = task_result.get("subtopics", [])
                    return [st.get("subtopic", "") for st in subtopics if st.get("subtopic")]
                else:
                    status_message = task.get("status_message", "Unknown error")
                    error_message = f"DataForSEO Content Generation API エラー (status_code: {status_code}): {status_message}"
                    
                    # Payment Requiredエラーの場合
                    if status_code == 40200:
                        error_message = f"DataForSEO Content Generation APIへのアクセス権限がありません（Payment Required）。DataForSEOアカウントに残高があるか確認してください。"
                    
                    raise Exception(error_message)
            
            # タスクが存在しない場合
            raise Exception("DataForSEO Content Generation API: レスポンスにタスクが含まれていません")
    except httpx.HTTPStatusError as e:
        error_message = f"DataForSEO Content Generation API HTTPエラー: {e.response.status_code} - {e.response.text[:500]}"
        raise Exception(error_message)
    except httpx.RequestError as e:
        error_message = f"DataForSEO Content Generation API リクエストエラー: {str(e)}"
        raise Exception(error_message)
    except Exception as e:
        # 既にExceptionの場合はそのまま再スロー
        raise


def generate_related_keywords_with_openai(
    main_keyword: str,
    important_keywords: List[str],
    secondary_keywords: List[str],
    openai_client
) -> List[str]:
    """
    OpenAIを使って関連キーワード100個を生成
    
    Args:
        main_keyword: メインキーワード
        important_keywords: 重要キーワードリスト
        secondary_keywords: サブキーワードリスト
        openai_client: OpenAIクライアント
    
    Returns:
        関連キーワードのリスト（100個）
    """
    all_input_keywords = [main_keyword] + important_keywords + secondary_keywords
    keywords_str = "、".join([kw for kw in all_input_keywords if kw])
    
    prompt = f"""
あなたはSEO専門家です。以下のキーワードに関連する、記事作成に最適なキーワードを100個生成してください。

入力キーワード:
{keywords_str}

要件:
- 検索意図が明確なキーワード
- 記事に自然に組み込めるキーワード
- 検索ボリュームが見込めるキーワード
- 関連性の高いキーワード
- 長尾キーワードも含める

出力形式:
1. キーワード1
2. キーワード2
3. キーワード3
...
100. キーワード100

番号とピリオド、キーワードのみを出力してください。説明は不要です。
"""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたはSEO専門家です。関連キーワードを生成してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        text = response.choices[0].message.content.strip()
        
        # 番号付きリストからキーワードを抽出
        keywords = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 番号とピリオドを除去
            if line and (line[0].isdigit() or line.startswith('-')):
                # "1. キーワード" または "- キーワード" の形式
                parts = line.split('.', 1)
                if len(parts) > 1:
                    keyword = parts[1].strip()
                else:
                    keyword = line.lstrip('- ').strip()
                if keyword:
                    keywords.append(keyword)
        
        # 100個に調整（足りない場合は重複を許可せず、多い場合は切り詰め）
        return keywords[:100]
    except Exception as e:
        print(f"OpenAIキーワード生成エラー: {str(e)}")
        return []


def score_keywords(keywords_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    キーワードデータをスコアリングして最適なキーワードを選定
    
    スコアリング基準:
    - 検索ボリュームが高い（最大100点）
    - 競合度が低い（最大100点）
    - 総合スコア = (検索ボリュームスコア × 0.6) + (競合度スコア × 0.4)
    
    Args:
        keywords_data: DataForSEO Keywords APIから取得したデータ
    
    Returns:
        スコアリング済みキーワードのリスト（スコア順）
    """
    if not keywords_data:
        return []
    
    scored_keywords = []
    
    for kw_data in keywords_data:
        keyword_info = kw_data.get("keyword_info", {})
        keyword = keyword_info.get("keyword", "")
        search_volume = keyword_info.get("search_volume", 0)
        competition_index = keyword_info.get("competition_index", 100)  # 0-100、高いほど競合が激しい
        cpc = keyword_info.get("cpc", 0)
        
        if not keyword:
            continue
        
        # 検索ボリュームスコア（0-100点）
        # 検索ボリュームが1000以上で100点、0で0点（対数スケール）
        if search_volume > 0:
            volume_score = min(100, (search_volume / 1000) * 100)
            # 対数スケールで正規化（より現実的）
            import math
            if search_volume >= 1000:
                volume_score = 100
            elif search_volume >= 100:
                volume_score = 70 + (search_volume - 100) / 900 * 30
            elif search_volume >= 10:
                volume_score = 40 + (search_volume - 10) / 90 * 30
            else:
                volume_score = search_volume / 10 * 40
        else:
            volume_score = 0
        
        # 競合度スコア（0-100点）
        # 競合度が低いほど高スコア（competition_indexが低いほど良い）
        competition_score = max(0, 100 - competition_index)
        
        # 総合スコア
        total_score = (volume_score * 0.6) + (competition_score * 0.4)
        
        scored_keywords.append({
            "keyword": keyword,
            "search_volume": search_volume,
            "competition_index": competition_index,
            "cpc": cpc,
            "volume_score": round(volume_score, 2),
            "competition_score": round(competition_score, 2),
            "total_score": round(total_score, 2)
        })
    
    # 総合スコアでソート（降順）
    scored_keywords.sort(key=lambda x: x["total_score"], reverse=True)
    
    return scored_keywords


def get_best_keywords(
    scored_keywords: List[Dict[str, Any]],
    top_n: int = 20
) -> List[Dict[str, Any]]:
    """
    最適なキーワードを上位N個取得
    
    Args:
        scored_keywords: スコアリング済みキーワードリスト
        top_n: 取得するキーワード数
    
    Returns:
        最適なキーワードのリスト
    """
    return scored_keywords[:top_n]


def analyze_serp_structure(serp_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    SERPデータから見出し構造、共通パターン、FAQを分析
    
    Args:
        serp_data: SERP APIから取得したデータ
    
    Returns:
        分析結果の辞書
    """
    if not serp_data:
        return {}
    
    organic_results = serp_data.get("items", [])
    faq_items = []
    common_headings = []
    headings_analysis = {
        "h1_patterns": [],
        "h2_patterns": [],
        "h3_patterns": []
    }
    
    # People Also Ask（PAA）の質問を抽出
    for item in organic_results:
        if item.get("type") == "people_also_ask":
            questions = item.get("items", [])
            for q in questions:
                if q.get("question"):
                    faq_items.append(q.get("question"))
    
    # 見出し構造を分析
    for item in organic_results:
        if item.get("type") == "organic":
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            
            # タイトルから見出しパターンを抽出
            if "とは" in title:
                headings_analysis["h1_patterns"].append("定義・説明型")
            if "選び方" in title or "方法" in title:
                headings_analysis["h2_patterns"].append("選び方・方法型")
            if "おすすめ" in title or "ランキング" in title:
                headings_analysis["h2_patterns"].append("おすすめ・ランキング型")
            if "比較" in title:
                headings_analysis["h2_patterns"].append("比較型")
    
    # 共通パターンを集計
    common_patterns = {
        "definition": len([h for h in headings_analysis["h1_patterns"] if h == "定義・説明型"]),
        "how_to": len([h for h in headings_analysis["h2_patterns"] if h == "選び方・方法型"]),
        "recommendation": len([h for h in headings_analysis["h2_patterns"] if h == "おすすめ・ランキング型"]),
        "comparison": len([h for h in headings_analysis["h2_patterns"] if h == "比較型"])
    }
    
    return {
        "headings_analysis": headings_analysis,
        "common_patterns": common_patterns,
        "faq_items": faq_items[:10],  # 上位10個
        "total_results": len(organic_results),
        "average_title_length": sum(len(item.get("title", "")) for item in organic_results if item.get("type") == "organic") / max(len([item for item in organic_results if item.get("type") == "organic"]), 1)
    }

