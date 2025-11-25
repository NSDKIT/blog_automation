"""
記事生成の非同期タスク
実際のワークフロー処理を実装
"""
from typing import Dict
from app.supabase_db import get_article_by_id, update_article
from app.workflow import ArticleGenerator

def generate_article_task(article_id: str, article_data: Dict):
    """
    記事生成のバックグラウンドタスク
    """
    try:
        # 記事を取得（user_idは不要なのでNoneを渡す）
        # 実際にはuser_idが必要だが、バックグラウンドタスクなので全ユーザーから検索
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
        user_id = article.get("user_id")
        
        # 記事生成ワークフローを実行
        generator = ArticleGenerator()
        result = generator.generate(article_data)
        
        # 結果を保存
        update_article(article_id, user_id, {
            "title": result.get("title"),
            "content": result.get("content"),
            "status": "completed"
        })
        
    except Exception as e:
        # エラー処理
        try:
            article_response = supabase.table("articles").select("*").eq("id", article_id).limit(1).execute()
            if article_response.data and len(article_response.data) > 0:
                article = article_response.data[0]
                update_article(article_id, article.get("user_id"), {"status": "failed"})
        except:
            pass
        print(f"記事生成エラー: {e}")

