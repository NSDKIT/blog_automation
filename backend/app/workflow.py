"""
元のワークフローを実装するクラス
メガネ記事案ジェネレーター.ymlのロジックを移植
SEO対策機能を統合
"""
import os
import re
import json
import httpx
import asyncio
from typing import Dict, List, Optional
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from app.supabase_client import get_supabase_client
from app.dataforseo_client import (
    get_serp_data, get_keywords_data, generate_meta_tags, 
    generate_subtopics, analyze_serp_structure,
    generate_related_keywords_with_openai, score_keywords, get_best_keywords
)
from app.schema_generator import generate_all_schemas

load_dotenv()


class ArticleGenerator:
    """記事生成ワークフロー"""
    
    def __init__(self, user_id: Optional[str] = None):
        """
        Args:
            user_id: ユーザーID（オプション、ユーザー設定を使用する場合に必要）
        """
        # 環境変数からAPIキーを取得（ユーザー設定がない場合のフォールバック）
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        self.supabase = get_supabase_client()  # Noneの可能性がある
        self.user_id = user_id
        
        # ユーザー設定からAPIキーを取得（設定されている場合）
        if user_id:
            from app.supabase_db import get_setting_by_key
            
            # OpenAI API Key
            user_openai_key = get_setting_by_key(user_id, "openai_api_key")
            if user_openai_key:
                self.openai_client = OpenAI(api_key=user_openai_key)
            
            # Gemini API Key
            user_gemini_key = get_setting_by_key(user_id, "gemini_api_key")
            if user_gemini_key:
                genai.configure(api_key=user_gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate(self, article_data: Dict) -> Dict:
        """
        記事生成のメイン処理（SEO対策統合版）
        """
        try:
            # SEO対策: 0. SERP分析（非同期）
            serp_data = None
            serp_analysis = {}
            keywords_data = None
            meta_tags = None
            subtopics_list = None
            best_keywords = []  # 最適なキーワードリスト（初期化）
            
            keyword = article_data.get("keyword")
            search_intent = article_data.get("search_intent", "情報収集")
            target_location = article_data.get("target_location", "Japan")
            device_type = article_data.get("device_type", "mobile")
            
            # 重要キーワードをリスト化
            important_keywords = [
                kw for kw in [
                    article_data.get("important_keyword1"),
                    article_data.get("important_keyword2"),
                    article_data.get("important_keyword3")
                ] if kw
            ]
            secondary_keywords = article_data.get("secondary_keywords", [])
            
            # ユーザーが選択したキーワードがある場合はそれを使用（キーワード選択機能経由）
            # 選択されたキーワードがない場合のみ、新規にキーワード生成・分析を行う
            keywords_data = None
            best_keywords = []
            
            # 選択されたキーワードがある場合は、それを使用してbest_keywordsを作成
            if secondary_keywords and len(secondary_keywords) > 0:
                print(f"選択されたキーワードを使用: {len(secondary_keywords)}個")
                # 選択されたキーワードをbest_keywords形式に変換
                best_keywords = [{"keyword": kw} for kw in secondary_keywords[:20]]
            else:
                # キーワード選択機能を使わない場合（後方互換性のため）
                try:
                    print("OpenAIで関連キーワード100個を生成中...")
                    related_keywords_100 = generate_related_keywords_with_openai(
                        main_keyword=keyword,
                        important_keywords=important_keywords,
                        secondary_keywords=secondary_keywords or [],
                        openai_client=self.openai_client
                    )
                    
                    if related_keywords_100:
                        print(f"生成されたキーワード数: {len(related_keywords_100)}")
                        
                        # DataForSEOで検索ボリューム・競合度を取得
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # 100個のキーワードをバッチで取得（DataForSEOは最大100個まで）
                        keywords_data = loop.run_until_complete(
                            get_keywords_data(
                                keywords=related_keywords_100[:100],
                                location_code=2840,
                                language_code="ja",
                                user_id=self.user_id
                            )
                        )
                        
                        if keywords_data:
                            # キーワードをスコアリング
                            scored_keywords = score_keywords(keywords_data)
                            
                            # 最適なキーワードを上位20個取得
                            best_keywords = get_best_keywords(scored_keywords, top_n=20)
                            print(f"最適なキーワードを{len(best_keywords)}個選定しました")
                        
                        loop.close()
                except Exception as e:
                    print(f"キーワード生成・分析エラー（続行）: {str(e)}")
                    # エラーが発生しても記事生成は続行
            
            # 元のキーワードも含める
            all_keywords = [keyword] + important_keywords + (secondary_keywords or [])
            if best_keywords:
                # 最適なキーワードの上位10個を追加
                best_keywords_list = [kw["keyword"] for kw in best_keywords[:10]]
                all_keywords.extend(best_keywords_list)
            
            try:
                # 非同期処理を同期的に実行
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # SERP分析
                serp_data = loop.run_until_complete(
                    get_serp_data(
                        keyword=keyword,
                        location_code=2840,  # 日本
                        language_code="ja",
                        device=device_type,
                        depth=50,
                        user_id=self.user_id
                    )
                )
                
                if serp_data:
                    serp_analysis = analyze_serp_structure(serp_data)
                
                # 元のキーワードのデータも取得（最適なキーワードと統合）
                if all_keywords and not keywords_data:
                    keywords_data = loop.run_until_complete(
                        get_keywords_data(
                            keywords=all_keywords[:100],  # 最大100個
                            location_code=2840,
                            language_code="ja",
                            user_id=self.user_id
                        )
                    )
                
                loop.close()
            except Exception as e:
                print(f"SEO分析エラー（続行）: {str(e)}")
                # SEO分析が失敗しても記事生成は続行
            
            # 1. 知識検索
            knowledge_context = self._knowledge_retrieval(keyword)
            
            # 2. Google検索（フォールバック、SERP APIが使えない場合）
            google_results = []
            if not serp_data:
                google_results = self._google_search(keyword)
            
            # 3. 記事分析（SERP分析結果またはGoogle検索結果を使用）
            if serp_analysis:
                analysis = {
                    "optimal_length": str(int(serp_analysis.get("average_title_length", 30) * 100)),
                    "common_words": ", ".join([
                        k for k, v in serp_analysis.get("common_patterns", {}).items() 
                        if v > 0
                    ]),
                    "summaries": json.dumps(serp_analysis, ensure_ascii=False),
                    "serp_analysis": serp_analysis
                }
            else:
            analysis = self._analyze_articles(google_results)
            
            # サブトピック生成
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                subtopics_list = loop.run_until_complete(
                    generate_subtopics(keyword, user_id=self.user_id)
                )
                loop.close()
            except Exception as e:
                print(f"サブトピック生成エラー（続行）: {str(e)}")
            
            # 4. タイトル生成（SEO最適化）
            title = self._generate_title_seo(
                article_data, knowledge_context, analysis, 
                serp_analysis, keywords_data, best_keywords
            )
            
            # 5. 記事生成（SEO最適化）
            content = self._generate_content_seo(
                article_data, title, knowledge_context, analysis,
                serp_analysis, keywords_data, subtopics_list, best_keywords
            )
            
            # 6. 画像選定
            images = self._select_images(keyword)
            
            # 7. 画像挿入
            content_with_images = self._insert_images(content, images)
            
            # メタタグ生成
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                meta_tags = loop.run_until_complete(
                    generate_meta_tags(title, content_with_images, user_id=self.user_id)
                )
                loop.close()
            except Exception as e:
                print(f"メタタグ生成エラー（続行）: {str(e)}")
            
            # 構造化データ生成
            faq_items = serp_analysis.get("faq_items", []) if serp_analysis else []
            structured_data = generate_all_schemas(
                title=title,
                content=content_with_images,
                faq_items=[{"question": q, "answer": ""} for q in faq_items] if faq_items else None
            )
            
            # 8. Shopify形式変換
            shopify_json = self._convert_to_shopify(content_with_images)
            
            return {
                "title": title,
                "content": content_with_images,
                "shopify_json": shopify_json,
                # SEO関連データ
                "meta_title": meta_tags.get("meta_title") if meta_tags else None,
                "meta_description": meta_tags.get("meta_description") if meta_tags else None,
                "serp_data": serp_data,
                "serp_headings_analysis": serp_analysis.get("headings_analysis") if serp_analysis else None,
                "serp_common_patterns": serp_analysis.get("common_patterns") if serp_analysis else None,
                "serp_faq_items": faq_items,
                "keyword_volume_data": keywords_data,
                "related_keywords": self._extract_related_keywords(keywords_data) if keywords_data else None,
                "keyword_difficulty": self._extract_keyword_difficulty(keywords_data) if keywords_data else None,
                "best_keywords": best_keywords,  # 最適なキーワードリスト（スコアリング済み）
                "subtopics": subtopics_list,
                "content_structure": serp_analysis.get("headings_analysis") if serp_analysis else None,
                "structured_data": structured_data,
                "search_intent": search_intent,
                "target_location": target_location,
                "device_type": device_type
            }
        except Exception as e:
            raise Exception(f"記事生成エラー: {str(e)}")
    
    def _knowledge_retrieval(self, keyword: str) -> str:
        """知識ベースから情報を取得（Supabase）"""
        if not self.supabase:
            # Supabaseが設定されていない場合は空文字列を返す
            print("警告: Supabaseが設定されていません。知識ベース検索をスキップします。")
            return ""
        
        try:
            # Supabaseのknowledge_baseテーブルから検索
            response = self.supabase.table("knowledge_base")\
                .select("*")\
                .ilike("content", f"%{keyword}%")\
                .limit(5)\
                .execute()
            
            if response.data:
                # 関連する知識を結合
                knowledge_texts = [item.get("content", "") for item in response.data]
                return "\n\n".join(knowledge_texts)
            return ""
        except Exception as e:
            print(f"知識ベース検索エラー: {e}")
            return ""
    
    def _google_search(self, keyword: str) -> List[Dict]:
        """Google検索を実行"""
        # Google Custom Search APIを使用
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": keyword,
            "num": 10
        }
        
        response = httpx.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        return []
    
    def _analyze_articles(self, google_results: List[Dict]) -> Dict:
        """検索結果を分析"""
        # 各URLからコンテンツを取得して分析
        articles_text = []
        for result in google_results[:10]:
            try:
                response = httpx.get(result.get("link"), timeout=10)
                if response.status_code == 200:
                    articles_text.append(response.text)
            except:
                continue
        
        # Geminiで分析
        prompt = f"""
        以下の10個のテキストファイルを分析し、以下の形式で出力してください。
        
        # 分析対象テキスト
        {json.dumps(articles_text[:10], ensure_ascii=False)}
        
        # 出力形式
        ・最適文字数：〇〇文字
        ・見出しによく使われているワード：〇〇、〇〇、〇〇
        ・各テキストファイルの概要：〇〇〜〜〜。〇〇〜〜〜〜。
        """
        
        response = self.gemini_model.generate_content(prompt)
        return {
            "optimal_length": self._extract_optimal_length(response.text),
            "common_words": self._extract_common_words(response.text),
            "summaries": response.text
        }
    
    def _generate_title_seo(
        self, 
        article_data: Dict, 
        knowledge_context: str, 
        analysis: Dict,
        serp_analysis: Dict,
        keywords_data: Optional[List[Dict]],
        best_keywords: List[Dict]
    ) -> str:
        """SEO最適化されたタイトルを生成"""
        # 最適なキーワードをプロンプトに追加
        best_keywords_str = ""
        if best_keywords:
            top_keywords = [kw["keyword"] for kw in best_keywords[:5]]
            best_keywords_str = f"\n\n# 最適なキーワード（スコアリング済み）\n優先的に使用すべきキーワード: {', '.join(top_keywords)}"
        
        # 既存のメソッドを呼び出し（プロンプトを拡張）
        # 一時的にarticle_dataに最適なキーワードを追加
        enhanced_article_data = article_data.copy()
        if best_keywords_str:
            # プロンプトに最適なキーワードを追加
            original_prompt = article_data.get("prompt", "")
            enhanced_article_data["prompt"] = (original_prompt + best_keywords_str) if original_prompt else best_keywords_str
        
        title = self._generate_title(enhanced_article_data, knowledge_context, analysis)
        
        # SERP分析結果があれば、見出しパターンを参考にする
        if serp_analysis:
            common_patterns = serp_analysis.get("common_patterns", {})
            # 最も多いパターンを参考にする
            if common_patterns.get("definition", 0) > 0:
                # 定義型のタイトルを推奨
                pass
            elif common_patterns.get("how_to", 0) > 0:
                # 方法型のタイトルを推奨
                pass
        
        return title
    
    def _generate_title(self, article_data: Dict, knowledge_context: str, analysis: Dict) -> str:
        """タイトルを生成"""
        prompt = f"""
        あなたは優秀なコンテンツマーケターです。以下の情報を基に、魅力的で読まれやすい記事のタイトル案を1個生成してください。
        
        # 眼鏡生産者の想い
        {knowledge_context}
        
        # Googleにおける記事の概要
        {analysis.get('summaries', '')}
        
        # 生成条件
        - 文字数: 15-40文字
        - ターゲット: {article_data.get('target')}
        - タイトルの種類・パターン: {article_data.get('article_type')}
        - 使用シーン: {article_data.get('used_type1', '')}
        
        # 重要なキーワード
        - {article_data.get('important_keyword1', '')}
        - {article_data.get('important_keyword2', '')}
        - {article_data.get('important_keyword3', '')}
        
        タイトル案を1つ出力してください。
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは優秀なコンテンツマーケターです。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_content_seo(
        self,
        article_data: Dict,
        title: str,
        knowledge_context: str,
        analysis: Dict,
        serp_analysis: Dict,
        keywords_data: Optional[List[Dict]],
        subtopics: Optional[List[str]],
        best_keywords: List[Dict]
    ) -> str:
        """SEO最適化された記事内容を生成"""
        # 最適なキーワードをプロンプトに追加
        best_keywords_str = ""
        if best_keywords:
            top_keywords = [kw["keyword"] for kw in best_keywords[:10]]
            best_keywords_str = f"\n\n# 最適なキーワード（スコアリング済み、優先的に使用）\n{', '.join(top_keywords)}\nこれらのキーワードを自然に記事本文に組み込んでください。"
        
        # 既存のメソッドを呼び出し（プロンプトを拡張）
        enhanced_article_data = article_data.copy()
        if best_keywords_str:
            original_prompt = article_data.get("prompt", "")
            enhanced_article_data["prompt"] = (original_prompt + best_keywords_str) if original_prompt else best_keywords_str
        
        content = self._generate_content(enhanced_article_data, title, knowledge_context, analysis)
        
        # SERP分析結果とサブトピックを活用してコンテンツを強化
        if serp_analysis or subtopics:
            # プロンプトを拡張して再生成（オプション）
            # 今回は既存の生成結果を使用
            pass
        
        return content
    
    def _generate_content(self, article_data: Dict, title: str, knowledge_context: str, analysis: Dict) -> str:
        """記事内容を生成"""
        prompt = f"""
        あなたは経験豊富なコンテンツライターです。与えられたタイトルに基づいて、魅力的な記事内容を生成してください。
        
        ## 入力データ
        ### 生成されたタイトル
        {title}
        
        # 眼鏡生産者の想い
        {knowledge_context}
        
        ### 必須単語
        {article_data.get('keyword')}
        
        ## 生成条件
        - 最適文字数: {analysis.get('optimal_length', '3000')}文字
        - 見出しによく使われるワード: {analysis.get('common_words', '')}
        - ターゲット読者: {article_data.get('target')}
        - 重要なキーワード: {article_data.get('important_keyword1', '')}, {article_data.get('important_keyword2', '')}, {article_data.get('important_keyword3', '')}
        
        ## 出力形式
        === 記事 ===
        [タイトル]
        ### [導入タイトル]
        [導入文]
        ### [本文タイトル]
        [本文]
        ### [まとめタイトル]
        [まとめ]
        """
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 4000,
                "temperature": 0.8,
            },
        )
        return response.text
    
    def _select_images(self, keyword: str) -> List[Dict]:
        """ユーザー登録の画像をキーワードで取得"""
        if not self.supabase or not self.user_id:
            # Supabaseが設定されていない、またはuser_idがない場合は空配列を返す
            print("警告: Supabaseが設定されていないか、user_idがありません。画像取得をスキップします。")
            return []
        
        try:
            # user_imagesテーブルからユーザーIDとキーワードで取得
            response = self.supabase.table("user_images")\
                .select("*")\
                .eq("user_id", self.user_id)\
                .eq("keyword", keyword)\
                .limit(20)\
                .execute()
            
            if response.data:
                # image_urlをurlに変換して既存の形式に合わせる
                return [
                    {
                        "url": img.get("image_url"),
                        "alt_text": img.get("alt_text", ""),
                        "id": img.get("id")
                    }
                    for img in response.data
                ]
            return []
        except Exception as e:
            print(f"画像取得エラー: {e}")
            return []
    
    def _insert_images(self, content: str, images: List[Dict]) -> str:
        """記事に画像を挿入"""
        # GPT-4oで画像を適切な位置に挿入
        prompt = f"""
        以下の記事に画像を適切な位置に挿入してください。
        
        記事内容:
        {content}
        
        画像データベース:
        {json.dumps(images, ensure_ascii=False)}
        
        Markdown形式で画像を ![alt](URL) の形式で挿入してください。
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは記事制作と画像選定の専門家です。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def _convert_to_shopify(self, content: str) -> Dict:
        """Shopify形式に変換"""
        prompt = f"""
        以下の記事を正しいShopify JSON形式に変換してください。
        
        ## 記事内容
        {content}
        
        ## 出力形式
        {{"article":{{"title":"記事タイトル","body_html":"<h2>見出し</h2><p>内容</p>","metafields_global_description_tag":"meta_text","status":"draft","published":false,"tags":"Column","author":"eightoon"}}}}
        
        1行のJSON形式で出力してください。
        """
        
        response = self.gemini_model.generate_content(prompt)
        json_str = self._extract_json_string(response.text)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as exc:
            snippet = (json_str[:200] + "...") if len(json_str) > 200 else json_str
            raise ValueError(f"GeminiレスポンスをJSONとして解析できません: {snippet}") from exc
    
    def _extract_optimal_length(self, text: str) -> str:
        """最適文字数を抽出"""
        # 実装が必要
        return "3000"
    
    def _extract_common_words(self, text: str) -> str:
        """頻出ワードを抽出"""
        # 実装が必要
        return "メガネ, 眼鏡, ブルーライト"

    def _extract_related_keywords(self, keywords_data: List[Dict]) -> List[Dict]:
        """キーワードデータから関連キーワードを抽出"""
        related_keywords = []
        if not keywords_data:
            return related_keywords
        
        for kw_data in keywords_data:
            if kw_data.get("keyword_info"):
                keyword = kw_data["keyword_info"].get("keyword", "")
                volume = kw_data["keyword_info"].get("search_volume", 0)
                cpc = kw_data["keyword_info"].get("cpc", 0)
                related_keywords.append({
                    "keyword": keyword,
                    "volume": volume,
                    "cpc": cpc
                })
        
        return related_keywords
    
    def _extract_keyword_difficulty(self, keywords_data: List[Dict]) -> Dict:
        """キーワードデータから難易度情報を抽出"""
        if not keywords_data or len(keywords_data) == 0:
            return {}
        
        first_keyword = keywords_data[0]
        keyword_info = first_keyword.get("keyword_info", {})
        
        return {
            "keyword": keyword_info.get("keyword", ""),
            "search_volume": keyword_info.get("search_volume", 0),
            "competition": keyword_info.get("competition", 0),
            "competition_index": keyword_info.get("competition_index", 0),
            "cpc": keyword_info.get("cpc", 0)
        }

    def _extract_json_string(self, raw_text: str) -> str:
        """GeminiのレスポンスからJSON文字列部分のみを抽出"""
        if not raw_text:
            raise ValueError("Geminiレスポンスが空です")
        
        text = raw_text.strip()
        if text.startswith("```"):
            # ```json ... ``` の形式を削除
            text = re.sub(r"^```(?:json)?", "", text, count=1).strip()
            if text.endswith("```"):
                text = text[:-3].strip()
        
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()
        return text

