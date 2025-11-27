"""
記事生成の非同期タスク
実際のワークフロー処理を実装
"""
import asyncio
import json
from typing import Dict, List
from app.supabase_db import update_article, create_article_history
from app.workflow import ArticleGenerator
from app.sanitize import sanitize_html
from app.dataforseo_client import (
    generate_related_keywords_with_openai,
    get_keywords_data,
    score_keywords,
    get_keywords_data_google_ads
)

def generate_article_task(article_id: str, article_data: Dict, user_id: str = None):
    """
    記事生成のバックグラウンドタスク
    
    Args:
        article_id: 記事ID
        article_data: 記事データ
        user_id: ユーザーID（オプション、指定されない場合は記事から取得）
    """
    try:
        # 記事を取得してuser_idを確認
        from app.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        if not supabase:
            print("Supabase client is not configured")
            return
        
        article_response = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
        if not article_response.data or len(article_response.data) == 0:
            print(f"Article not found: {article_id}")
            return
        
        article = article_response.data[0]
        if not user_id:
            user_id = article.get("user_id")
        
        # 記事生成ワークフローを実行（user_idを渡す）
        generator = ArticleGenerator(user_id=user_id)
        result = generator.generate(article_data)
        
        # 結果を保存
        sanitized_content = sanitize_html(result.get("content"))
        updates = {
            "title": result.get("title"),
            "content": sanitized_content,
            "status": "completed",
            "error_message": None
        }
        
        # shopify_jsonがあればJSON文字列として保存
        if result.get("shopify_json"):
            import json
            updates["shopify_json"] = json.dumps(result.get("shopify_json"), ensure_ascii=False)
        
        # SEO関連データを保存
        if result.get("meta_title"):
            updates["meta_title"] = result.get("meta_title")
        if result.get("meta_description"):
            updates["meta_description"] = result.get("meta_description")
        if result.get("serp_data"):
            updates["serp_data"] = json.dumps(result.get("serp_data"), ensure_ascii=False)
        if result.get("serp_headings_analysis"):
            updates["serp_headings_analysis"] = json.dumps(result.get("serp_headings_analysis"), ensure_ascii=False)
        if result.get("serp_common_patterns"):
            updates["serp_common_patterns"] = json.dumps(result.get("serp_common_patterns"), ensure_ascii=False)
        if result.get("serp_faq_items"):
            updates["serp_faq_items"] = json.dumps(result.get("serp_faq_items"), ensure_ascii=False)
        if result.get("keyword_volume_data"):
            updates["keyword_volume_data"] = json.dumps(result.get("keyword_volume_data"), ensure_ascii=False)
        if result.get("related_keywords"):
            updates["related_keywords"] = json.dumps(result.get("related_keywords"), ensure_ascii=False)
        if result.get("keyword_difficulty"):
            updates["keyword_difficulty"] = json.dumps(result.get("keyword_difficulty"), ensure_ascii=False)
        if result.get("subtopics"):
            updates["subtopics"] = json.dumps(result.get("subtopics"), ensure_ascii=False)
        if result.get("content_structure"):
            updates["content_structure"] = json.dumps(result.get("content_structure"), ensure_ascii=False)
        if result.get("structured_data"):
            updates["structured_data"] = json.dumps(result.get("structured_data"), ensure_ascii=False)
        if result.get("search_intent"):
            updates["search_intent"] = result.get("search_intent")
        if result.get("target_location"):
            updates["target_location"] = result.get("target_location")
        if result.get("device_type"):
            updates["device_type"] = result.get("device_type")
        if result.get("best_keywords"):
            updates["best_keywords"] = json.dumps(result.get("best_keywords"), ensure_ascii=False)
        
        update_article(article_id, user_id, updates)
        
    except Exception as e:
        # エラー処理
        error_message = str(e)
        try:
            article_response = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
            if article_response.data and len(article_response.data) > 0:
                article = article_response.data[0]
                update_article(
                    article_id,
                    article.get("user_id"),
                    {"status": "failed", "error_message": error_message[:1000]}
                )
                create_article_history(
                    article_id=article_id,
                    action="failed",
                    changes={"error_message": error_message[:1000]}
                )
        except:
            pass
        print(f"記事生成エラー: {error_message}")


def analyze_keywords_task(article_id: str, article_data: Dict, user_id: str = None):
    """
    キーワード分析のバックグラウンドタスク
    関連キーワード100個を生成し、検索ボリューム・競合度を取得
    
    Args:
        article_id: 記事ID
        article_data: 記事データ
        user_id: ユーザーID（オプション、指定されない場合は記事から取得）
    """
    print(f"[analyze_keywords_task] 開始: article_id={article_id}, user_id={user_id}")
    try:
        # 記事を取得してuser_idを確認
        from app.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        if not supabase:
            print("[analyze_keywords_task] エラー: Supabase client is not configured")
            update_article(article_id, user_id, {"status": "failed", "error_message": "Supabase client is not configured"})
            return
        
        article_response = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
        if not article_response.data or len(article_response.data) == 0:
            print(f"[analyze_keywords_task] エラー: Article not found: {article_id}")
            return
        
        article = article_response.data[0]
        if not user_id:
            user_id = article.get("user_id")
        
        print(f"[analyze_keywords_task] 記事を取得: status={article.get('status')}, keyword={article.get('keyword')}")
        
        # OpenAIクライアントを取得
        from app.workflow import ArticleGenerator
        generator = ArticleGenerator(user_id=user_id)
        
        keyword = article_data.get("keyword")
        important_keywords = [
            kw for kw in [
                article_data.get("important_keyword1"),
                article_data.get("important_keyword2"),
                article_data.get("important_keyword3")
            ] if kw
        ]
        secondary_keywords = article_data.get("secondary_keywords", [])
        
        # OpenAIで関連キーワード100個を生成
        print(f"[analyze_keywords_task] OpenAIで関連キーワード100個を生成中... keyword={keyword}")
        related_keywords_100 = generate_related_keywords_with_openai(
            main_keyword=keyword,
            important_keywords=important_keywords,
            secondary_keywords=secondary_keywords or [],
            openai_client=generator.openai_client
        )
        
        if not related_keywords_100:
            print("[analyze_keywords_task] エラー: キーワード生成に失敗しました")
            update_article(
                article_id,
                user_id,
                {"status": "failed", "error_message": "キーワード生成に失敗しました"}
            )
            return
        
        print(f"[analyze_keywords_task] 生成されたキーワード数: {len(related_keywords_100)}")
        
        # DataForSEOで検索ボリューム・競合度を取得（ハイブリッド方式）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # ステップ1: dataforseo_labsで100個のキーワードを広く分析（コスト抑制）
            print(f"[analyze_keywords_task] dataforseo_labsで100個のキーワードを分析中...")
            keywords_data = loop.run_until_complete(
                get_keywords_data(
                    keywords=related_keywords_100[:100],
                    location_code=2840,
                    language_code="ja",
                    user_id=user_id
                )
            )
            
            if not keywords_data:
                print("[analyze_keywords_task] エラー: キーワードデータの取得に失敗しました")
                update_article(
                    article_id,
                    user_id,
                    {"status": "failed", "error_message": "キーワードデータの取得に失敗しました"}
                )
                return
            
            print(f"[analyze_keywords_task] キーワードデータを取得: {len(keywords_data)}個")
            
            # ステップ2: 初期スコアリング
            scored_keywords = score_keywords(keywords_data)
            
            # ステップ3: 上位20個のキーワードをGoogle Ads APIで再分析（より正確なデータ）
            if len(scored_keywords) >= 20:
                top_20_keywords = [kw["keyword"] for kw in scored_keywords[:20]]
                print(f"Google Ads APIで上位20個のキーワードを再分析中...")
                
                try:
                    from app.dataforseo_client import get_keywords_data_google_ads
                    google_ads_data = loop.run_until_complete(
                        get_keywords_data_google_ads(
                            keywords=top_20_keywords,
                            location_code=2840,
                            language_code="ja",
                            user_id=user_id
                        )
                    )
                    
                    # Google Ads APIのデータで上位20個を更新
                    if google_ads_data:
                        # Google Ads APIのデータ構造をdataforseo_labs形式に変換
                        google_ads_dict = {}
                        for item in google_ads_data:
                            kw_info = item.get("keyword_info", {})
                            keyword = kw_info.get("keyword", "")
                            if keyword:
                                google_ads_dict[keyword] = {
                                    "keyword_info": kw_info
                                }
                        
                        # 上位20個のキーワードデータを更新
                        for i, kw in enumerate(scored_keywords[:20]):
                            keyword = kw["keyword"]
                            if keyword in google_ads_dict:
                                # Google Ads APIのデータで更新
                                updated_data = google_ads_dict[keyword]
                                updated_kw_info = updated_data.get("keyword_info", {})
                                
                                # より正確なデータで更新
                                scored_keywords[i]["search_volume"] = updated_kw_info.get("search_volume", kw.get("search_volume", 0))
                                scored_keywords[i]["competition_index"] = updated_kw_info.get("competition_index", kw.get("competition_index", 100))
                                scored_keywords[i]["cpc"] = updated_kw_info.get("cpc", kw.get("cpc", 0))
                                
                                # スコアを再計算
                                search_volume = scored_keywords[i]["search_volume"]
                                competition_index = scored_keywords[i]["competition_index"]
                                
                                # 検索ボリュームスコア
                                if search_volume > 0:
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
                                
                                # 競合度スコア
                                competition_score = max(0, 100 - competition_index)
                                
                                # 総合スコア
                                total_score = (volume_score * 0.6) + (competition_score * 0.4)
                                
                                scored_keywords[i]["volume_score"] = round(volume_score, 2)
                                scored_keywords[i]["competition_score"] = round(competition_score, 2)
                                scored_keywords[i]["total_score"] = round(total_score, 2)
                        
                        # スコアで再ソート
                        scored_keywords.sort(key=lambda x: x["total_score"], reverse=True)
                        print(f"Google Ads APIで上位20個のキーワードを更新しました")
                    else:
                        print("Google Ads API: データが取得できませんでした。dataforseo_labsのデータを使用します")
                except Exception as google_ads_error:
                    # Google Ads APIが失敗した場合、エラーを記録してdataforseo_labsのデータを使用
                    error_msg = str(google_ads_error)
                    print(f"Google Ads API エラー: {error_msg}")
                    print("dataforseo_labsのデータを使用して続行します")
                    # エラーを記事のメタデータに保存（オプション）
                    # ここではログに記録するだけ
            
            # 全てのキーワードデータを保存（ユーザーが選択できるように）
            updates = {
                "status": "keyword_selection",  # キーワード選択待ち
                "analyzed_keywords": json.dumps(scored_keywords, ensure_ascii=False)
            }
            print(f"[analyze_keywords_task] ステータスを更新: keyword_selection, キーワード数: {len(scored_keywords)}")
            update_article(article_id, user_id, updates)
            print(f"[analyze_keywords_task] キーワード分析完了: {len(scored_keywords)}個のキーワードを分析しました")
        finally:
            loop.close()
            
    except Exception as e:
        error_message = str(e)
        import traceback
        print(f"[analyze_keywords_task] エラー発生: {error_message}")
        print(f"[analyze_keywords_task] トレースバック:\n{traceback.format_exc()}")
        try:
            from app.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                article_response = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
                if article_response.data and len(article_response.data) > 0:
                    article = article_response.data[0]
                    update_article(
                        article_id,
                        article.get("user_id"),
                        {"status": "failed", "error_message": error_message[:1000]}
                    )
                    print(f"[analyze_keywords_task] エラーを記事に保存しました")
        except Exception as update_error:
            print(f"[analyze_keywords_task] エラー保存に失敗: {str(update_error)}")
        print(f"[analyze_keywords_task] キーワード分析エラー: {error_message}")
