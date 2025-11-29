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


def extract_related_keywords(serp_data: Dict, keyword: str) -> Dict:
    """関連キーワードを抽出（Phase 2）"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    related_keywords = []
    
    # Related Searchesから抽出
    for item in items:
        if item.get("type") == "related_searches":
            searches = item.get("items", [])
            for s in searches:
                query = s.get("text", "")
                if query and query != keyword:
                    related_keywords.append({
                        "keyword": query,
                        "type": "related_search",
                        "priority": "high" if len(query.split()) <= 3 else "medium"
                    })
    
    # タイトルからも関連キーワードを抽出
    organic_items = [item for item in items if item.get("type") == "organic"]
    title_keywords = []
    for item in organic_items[:10]:
        title = item.get("title", "")
        # タイトルから重要な単語を抽出
        words = re.findall(r'\b\w+\b', title)
        for word in words:
            if len(word) >= 2 and word not in ["の", "は", "を", "に", "が", "と", "で", "も", "から", "まで"]:
                if word not in [kw["keyword"] for kw in related_keywords]:
                    title_keywords.append(word)
    
    # 頻度でソート
    keyword_counter = Counter(title_keywords)
    for word, count in keyword_counter.most_common(10):
        related_keywords.append({
            "keyword": word,
            "type": "title_extraction",
            "priority": "medium",
            "frequency": count
        })
    
    return {
        "related_keywords": related_keywords[:20],  # 最大20件
        "total_count": len(related_keywords)
    }


def analyze_keyword_density(serp_data: Dict, keyword: str) -> Dict:
    """キーワード密度を分析（Phase 2）"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    organic_items = [item for item in items if item.get("type") == "organic"]
    
    keyword_densities = []
    keyword_positions = []
    
    for item in organic_items[:10]:  # 上位10件を分析
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        text = f"{title} {snippet}"
        
        # キーワードの出現回数
        keyword_count = text.lower().count(keyword.lower())
        total_words = len(text.split())
        density = (keyword_count / total_words * 100) if total_words > 0 else 0
        
        # キーワードの位置（タイトル内かどうか）
        in_title = keyword.lower() in title.lower()
        in_snippet = keyword.lower() in snippet.lower()
        
        keyword_densities.append(density)
        keyword_positions.append({
            "in_title": in_title,
            "in_snippet": in_snippet,
            "density": round(density, 2)
        })
    
    avg_density = sum(keyword_densities) / len(keyword_densities) if keyword_densities else 0
    
    return {
        "average_density": round(avg_density, 2),
        "recommended_density": {
            "min": max(0.5, avg_density * 0.8),
            "max": min(2.5, avg_density * 1.2)
        },
        "keyword_positions": keyword_positions,
        "recommendation": "タイトルと最初の段落にキーワードを含めることを推奨します"
    }


def analyze_competitors(serp_data: Dict, keyword: str) -> Dict:
    """競合記事を分析（Phase 3）"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    organic_items = [item for item in items if item.get("type") == "organic"]
    
    competitor_analysis = []
    all_topics = []
    
    for idx, item in enumerate(organic_items[:10], 1):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        url = item.get("url", "")
        
        # 記事の特徴を抽出
        features = []
        if "おすすめ" in title or "ランキング" in title:
            features.append("ランキング形式")
        if "比較" in title:
            features.append("比較記事")
        if "選び方" in title or "方法" in title:
            features.append("ガイド記事")
        if "レビュー" in title or "口コミ" in title:
            features.append("レビュー記事")
        
        # トピックを抽出（タイトルとスニペットから）
        topics = []
        if "価格" in title or "値段" in snippet:
            topics.append("価格")
        if "特徴" in title or "メリット" in snippet:
            topics.append("特徴・メリット")
        if "デメリット" in snippet or "注意点" in snippet:
            topics.append("デメリット・注意点")
        if "選び方" in title or "ポイント" in snippet:
            topics.append("選び方")
        
        all_topics.extend(topics)
        
        competitor_analysis.append({
            "position": idx,
            "title": title,
            "snippet": snippet[:200],  # 最初の200文字
            "url": url,
            "features": features,
            "topics": topics,
            "title_length": len(title),
            "snippet_length": len(snippet)
        })
    
    # 全記事でカバーされているトピック
    topic_counter = Counter(all_topics)
    common_topics = [topic for topic, count in topic_counter.items() if count >= 5]
    rare_topics = [topic for topic, count in topic_counter.items() if count <= 2]
    
    return {
        "competitors": competitor_analysis,
        "common_topics": common_topics,  # 多くの記事でカバーされているトピック
        "rare_topics": rare_topics,  # 少数の記事のみでカバーされているトピック
        "content_gaps": rare_topics,  # コンテンツギャップ（差別化のチャンス）
        "differentiation_strategy": {
            "focus_areas": rare_topics[:3],  # 差別化すべきトピック
            "must_include": common_topics[:5],  # 必ず含めるべきトピック
            "recommendation": f"「{', '.join(rare_topics[:3])}」に焦点を当てることで差別化できます"
        }
    }


def analyze_search_intent(serp_data: Dict) -> Dict:
    """検索意図を分析（Phase 3）"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    organic_items = [item for item in items if item.get("type") == "organic"]
    
    intent_signals = {
        "informational": 0,  # 情報収集
        "commercial": 0,  # 購買検討
        "transactional": 0,  # 購入
        "navigational": 0  # 特定サイトへのアクセス
    }
    
    article_types = []
    
    for item in organic_items[:10]:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        
        # 検索意図の判定
        if "とは" in title or "意味" in title or "定義" in title:
            intent_signals["informational"] += 1
            article_types.append("ガイド記事")
        if "おすすめ" in title or "ランキング" in title or "比較" in title:
            intent_signals["commercial"] += 1
            article_types.append("比較・ランキング記事")
        if "購入" in title or "買う" in title or "通販" in snippet:
            intent_signals["transactional"] += 1
            article_types.append("購入記事")
        if "公式" in title or "サイト" in title:
            intent_signals["navigational"] += 1
    
    # 最も多い検索意図を判定
    dominant_intent = max(intent_signals, key=intent_signals.get)
    intent_mapping = {
        "informational": "情報収集",
        "commercial": "購買検討",
        "transactional": "購入",
        "navigational": "特定サイトへのアクセス"
    }
    
    article_type_counter = Counter(article_types)
    recommended_type = article_type_counter.most_common(1)[0][0] if article_type_counter else "ガイド記事"
    
    return {
        "dominant_intent": intent_mapping.get(dominant_intent, "情報収集"),
        "intent_scores": intent_signals,
        "recommended_article_type": recommended_type,
        "confidence": max(intent_signals.values()) / sum(intent_signals.values()) * 100 if sum(intent_signals.values()) > 0 else 0
    }


def generate_prompt(seo_analysis: Dict, keyword: str) -> Dict:
    """記事生成用のプロンプトを自動生成（Phase 4）"""
    if not seo_analysis:
        return {}
    
    headings = seo_analysis.get("headings_analysis", {})
    titles = seo_analysis.get("titles_analysis", {})
    faq = seo_analysis.get("faq_items", [])
    keywords = seo_analysis.get("keyword_optimization", {})
    competitors = seo_analysis.get("competitor_analysis", {})
    intent = seo_analysis.get("search_intent", {})
    
    # 見出し構造テンプレート
    h2_patterns = headings.get("h2_patterns", {})
    recommended_headings = list(h2_patterns.keys())[:5]
    
    # FAQ項目
    faq_questions = [item.get("question", "") for item in faq[:5]]
    
    # 推奨キーワード
    related_kws = keywords.get("related_keywords", {}).get("related_keywords", [])
    recommended_keywords = [kw.get("keyword", "") for kw in related_kws[:10]]
    
    # 差別化ポイント
    diff_strategy = competitors.get("differentiation_strategy", {})
    focus_areas = diff_strategy.get("focus_areas", [])
    
    prompt_template = f"""
以下のSEO分析結果に基づいて、最高のSEO対策が施された記事を生成してください。

【メインキーワード】
{keyword}

【推奨見出し構造】
{chr(10).join([f"- {h}" for h in recommended_headings])}

【含めるべきFAQ項目】
{chr(10).join([f"- {q}" for q in faq_questions])}

【推奨関連キーワード】
{', '.join(recommended_keywords)}

【差別化ポイント】
{', '.join(focus_areas)}に焦点を当てて、競合記事との差別化を図ってください。

【検索意図】
{intent.get("dominant_intent", "情報収集")} - {intent.get("recommended_article_type", "ガイド記事")}形式で作成してください。

【タイトル推奨】
{titles.get("title_suggestions", [{}])[0].get("example", "") if titles.get("title_suggestions") else ""}
"""
    
    return {
        "prompt": prompt_template.strip(),
        "recommended_headings": recommended_headings,
        "faq_questions": faq_questions,
        "recommended_keywords": recommended_keywords,
        "focus_areas": focus_areas
    }


def suggest_structured_data(serp_data: Dict, faq_items: List[Dict]) -> Dict:
    """構造化データの提案（Phase 4）"""
    if not serp_data:
        return {}
    
    items = serp_data.get("items", [])
    
    # Featured Snippetの有無を確認
    has_featured_snippet = any(item.get("type") == "featured_snippet" for item in items)
    
    # FAQ構造化データの必要性
    needs_faq_schema = len(faq_items) >= 3
    
    # Article構造化データの必要性
    organic_items = [item for item in items if item.get("type") == "organic"]
    needs_article_schema = len(organic_items) > 0
    
    suggestions = []
    
    if needs_faq_schema:
        suggestions.append({
            "type": "FAQPage",
            "priority": "high",
            "reason": "People Also Askが3件以上あるため、FAQ構造化データを推奨します",
            "example": {
                "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q.get("question", ""), "acceptedAnswer": {"@type": "Answer", "text": q.get("answer", "")}} for q in faq_items[:5]]
            }
        })
    
    if needs_article_schema:
        suggestions.append({
            "type": "Article",
            "priority": "medium",
            "reason": "記事コンテンツの構造化データを推奨します",
            "example": {
                "@type": "Article",
                "headline": "記事タイトル",
                "author": {"@type": "Person", "name": "著者名"},
                "datePublished": "2025-01-01",
                "dateModified": "2025-01-01"
            }
        })
    
    if has_featured_snippet:
        suggestions.append({
            "type": "HowTo",
            "priority": "medium",
            "reason": "Featured Snippetが表示されているため、HowTo構造化データを検討してください"
        })
    
    return {
        "suggestions": suggestions,
        "has_featured_snippet": has_featured_snippet,
        "needs_faq_schema": needs_faq_schema,
        "needs_article_schema": needs_article_schema
    }


def analyze_device_differences(all_results: List[Dict]) -> Dict:
    """デバイス別の違いを分析（Phase 4）"""
    if not all_results or len(all_results) < 2:
        return {}
    
    # デスクトップとモバイルの結果を比較
    desktop_results = [r for r in all_results if "desktop" in r.get("url", "").lower()]
    mobile_results = [r for r in all_results if "mobile" in r.get("url", "").lower()]
    
    if not desktop_results or not mobile_results:
        return {}
    
    # 簡易的な比較（実際の実装では、SERPデータを詳細に比較）
    return {
        "has_differences": True,
        "recommendation": "モバイルとデスクトップで検索結果が異なる可能性があります。モバイルファーストのSEO対策を推奨します。",
        "mobile_optimization": [
            "ページ読み込み速度の最適化",
            "レスポンシブデザインの確認",
            "モバイルでのユーザビリティ向上"
        ]
    }


def analyze_serp_for_seo(serp_data: Dict, keyword: str) -> Dict:
    """SERPデータをSEO対策向けに分析（全機能統合）"""
    if not serp_data:
        return {}
    
    headings_analysis = analyze_headings_structure(serp_data)
    titles_analysis = analyze_titles(serp_data)
    faq_items = extract_faq_items(serp_data)
    
    # Phase 2: キーワード最適化
    keyword_optimization = {
        "related_keywords": extract_related_keywords(serp_data, keyword),
        "keyword_density": analyze_keyword_density(serp_data, keyword)
    }
    
    # Phase 3: 競合分析
    competitor_analysis = analyze_competitors(serp_data, keyword)
    search_intent = analyze_search_intent(serp_data)
    
    # Phase 4: 統合機能
    structured_data = suggest_structured_data(serp_data, faq_items)
    
    # プロンプト生成用のデータを準備
    seo_data_for_prompt = {
        "headings_analysis": headings_analysis,
        "titles_analysis": titles_analysis,
        "faq_items": faq_items,
        "keyword_optimization": keyword_optimization,
        "competitor_analysis": competitor_analysis,
        "search_intent": search_intent
    }
    prompt_generation = generate_prompt(seo_data_for_prompt, keyword)
    
    return {
        "headings_analysis": headings_analysis,
        "titles_analysis": titles_analysis,
        "faq_items": faq_items,
        "keyword_optimization": keyword_optimization,
        "competitor_analysis": competitor_analysis,
        "search_intent": search_intent,
        "structured_data": structured_data,
        "prompt_generation": prompt_generation
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
                seo_analysis = analyze_serp_for_seo(serp_data, keyword)
            
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
