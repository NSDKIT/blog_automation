"""
記事生成の非同期タスク
実際のワークフロー処理を実装
"""
from typing import Dict
from app.supabase_db import get_article_by_id, update_article
from app.workflow import ArticleGenerator

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
        updates = {
            "title": result.get("title"),
            "content": result.get("content"),
            "status": "completed",
            "error_message": None
        }
        
        # shopify_jsonがあればJSON文字列として保存
        if result.get("shopify_json"):
            import json
            updates["shopify_json"] = json.dumps(result.get("shopify_json"), ensure_ascii=False)
        
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
        except:
            pass
        print(f"記事生成エラー: {error_message}")

