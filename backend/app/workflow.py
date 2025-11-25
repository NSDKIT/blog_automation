"""
元のワークフローを実装するクラス
メガネ記事案ジェネレーター.ymlのロジックを移植
"""
import os
import re
import json
import httpx
from typing import Dict, List, Optional
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
from app.supabase_client import get_supabase_client

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
        記事生成のメイン処理
        """
        try:
            # 1. 知識検索
            knowledge_context = self._knowledge_retrieval(article_data.get("keyword"))
            
            # 2. Google検索
            google_results = self._google_search(article_data.get("keyword"))
            
            # 3. 記事分析
            analysis = self._analyze_articles(google_results)
            
            # 4. タイトル生成
            title = self._generate_title(article_data, knowledge_context, analysis)
            
            # 5. 記事生成
            content = self._generate_content(article_data, title, knowledge_context, analysis)
            
            # 6. 画像選定
            images = self._select_images(article_data.get("sheet_id"))
            
            # 7. 画像挿入
            content_with_images = self._insert_images(content, images)
            
            # 8. Shopify形式変換
            shopify_json = self._convert_to_shopify(content_with_images)
            
            return {
                "title": title,
                "content": content_with_images,
                "shopify_json": shopify_json
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
    
    def _select_images(self, sheet_id: str) -> List[Dict]:
        """Supabaseから画像を取得"""
        if not self.supabase:
            # Supabaseが設定されていない場合は空配列を返す
            print("警告: Supabaseが設定されていません。画像取得をスキップします。")
            return []
        
        try:
            # Supabaseのimagesテーブルから取得
            # sheet_idはキーワードやカテゴリとして使用
            response = self.supabase.table("images")\
                .select("*")\
                .eq("category", sheet_id)\
                .limit(20)\
                .execute()
            
            if response.data:
                return response.data
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

