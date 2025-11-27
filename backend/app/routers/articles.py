from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from typing import List
from uuid import UUID
from pydantic import BaseModel
import requests
from app.supabase_db import (
    get_articles_by_user_id, get_article_by_id, create_article,
    update_article, delete_article, create_article_history, create_audit_log
)
from app.schemas import ArticleCreate, ArticleResponse, ArticleUpdate
from app.dependencies import get_current_user
from app.tasks import generate_article_task
from app.rate_limit import rate_limit
from app.sanitize import sanitize_html
from app.utils import get_client_ip

router = APIRouter()


@router.get("", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    articles = get_articles_by_user_id(str(current_user.get("id")), skip, limit)
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    return article


@router.post(
    "",
    response_model=ArticleResponse,
    dependencies=[Depends(rate_limit(limit=5, window_seconds=60))]
)
async def create_article_endpoint(
    article_data: ArticleCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # 記事レコードを作成
    article = create_article(
        user_id=str(current_user.get("id")),
        keyword=article_data.keyword,
        target=article_data.target,
        article_type=article_data.article_type,
        status="keyword_analysis"  # キーワード分析待ちのステータス
    )
    
    # 初期進捗状況を設定
    import json
    initial_progress = {
        "status_check": False,
        "openai_generation": False,
        "dataforseo_fetch": False,
        "scoring_completed": False,
        "current_step": "status_check",
        "error_message": None
    }
    update_article(
        article.get("id"),
        str(current_user.get("id")),
        {"keyword_analysis_progress": json.dumps(initial_progress, ensure_ascii=False)}
    )
    
    # 履歴を記録
    create_article_history(
        article_id=article.get("id"),
        action="created",
        changes={"keyword": article_data.keyword, "target": article_data.target}
    )
    
    # バックグラウンドでキーワード分析を開始（別スレッドで実行して確実に実行されるように）
    from app.tasks import analyze_keywords_task
    import traceback
    import threading
    
    print(f"[create_article_endpoint] キーワード分析タスクを開始: article_id={article.get('id')}, status={article.get('status')}")
    
    # 記事のステータスを確認
    article_check = get_article_by_id(article.get("id"), str(current_user.get("id")))
    print(f"[create_article_endpoint] 記事確認: status={article_check.get('status') if article_check else 'None'}")
    
    # 別スレッドで実行（確実に実行されるように）
    def run_analyze_task():
        try:
            print(f"[create_article_endpoint] 別スレッドでキーワード分析タスクを開始")
            analyze_keywords_task(
                article_id=article.get("id"),
                article_data=article_data.dict(),
                user_id=str(current_user.get("id"))
            )
        except Exception as e:
            print(f"[create_article_endpoint] 別スレッドでのタスク実行エラー: {str(e)}")
            print(f"[create_article_endpoint] トレースバック:\n{traceback.format_exc()}")
    
    # 別スレッドで実行（非同期、daemon=Trueでメインスレッド終了時に自動終了）
    thread = threading.Thread(target=run_analyze_task, daemon=True)
    thread.start()
    print(f"[create_article_endpoint] 別スレッドでキーワード分析タスクを開始しました（スレッドID: {thread.ident}）")
    
    # FastAPIのBackgroundTasksにも追加（念のため）
    try:
        background_tasks.add_task(
            analyze_keywords_task,
            article_id=article.get("id"),
            article_data=article_data.dict(),
            user_id=str(current_user.get("id"))
        )
        print(f"[create_article_endpoint] キーワード分析タスクをBackgroundTasksにも追加しました")
    except Exception as e:
        print(f"[create_article_endpoint] BackgroundTasks追加エラー: {str(e)}")
        print(f"[create_article_endpoint] トレースバック:\n{traceback.format_exc()}")
        # エラーが発生した場合でも、別スレッドで実行されているので問題なし
    create_audit_log(
        user_id=str(current_user.get("id")),
        action="article_created",
        metadata={"article_id": article.get("id"), "keyword": article_data.keyword},
        ip_address=get_client_ip(request)
    )
    
    return article


@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
    dependencies=[Depends(rate_limit(limit=20, window_seconds=60))]
)
async def update_article_endpoint(
    article_id: UUID,
    article_update: ArticleUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # 既存の記事を取得
    existing_article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    # 更新内容を準備
    updates = {}
    changes = {}
    
    if article_update.title is not None:
        changes["title"] = {"old": existing_article.get("title"), "new": article_update.title}
        updates["title"] = article_update.title
    
    if article_update.content is not None:
        sanitized = sanitize_html(article_update.content)
        changes["content"] = {"old": existing_article.get("content"), "new": sanitized}
        updates["content"] = sanitized
    
    if article_update.status is not None:
        changes["status"] = {"old": existing_article.get("status"), "new": article_update.status}
        updates["status"] = article_update.status
    
    # 記事を更新
    article = update_article(str(article_id), str(current_user.get("id")), updates)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記事の更新に失敗しました"
        )
    
    # 履歴を記録
    if changes:
        create_article_history(
            article_id=str(article_id),
            action="updated",
            changes=changes
        )
        create_audit_log(
            user_id=str(current_user.get("id")),
            action="article_updated",
            metadata={"article_id": str(article_id), "fields": list(changes.keys())},
            ip_address=get_client_ip(request)
        )
    
    return article


@router.delete(
    "/{article_id}",
    dependencies=[Depends(rate_limit(limit=20, window_seconds=60))]
)
async def delete_article_endpoint(
    article_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # 既存の記事を確認
    existing_article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    # 履歴を記録
    create_article_history(
        article_id=str(article_id),
        action="deleted"
    )
    
    # 記事を削除
    delete_article(str(article_id), str(current_user.get("id")))
    create_audit_log(
        user_id=str(current_user.get("id")),
        action="article_deleted",
        metadata={"article_id": str(article_id)},
        ip_address=get_client_ip(request)
    )
    
    return {"message": "記事を削除しました"}


@router.post(
    "/{article_id}/publish",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=300))]
)
async def publish_article_endpoint(
    article_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    from app.shopify_client import publish_article_to_shopify
    import json
    
    article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    if not article.get("content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="記事内容が生成されていません"
        )
    
    user_id = str(current_user.get("id"))
    title = article.get("title", "タイトルなし")
    content = article.get("content", "")
    
    # shopify_jsonがあれば使用
    shopify_json = None
    if article.get("shopify_json"):
        try:
            if isinstance(article.get("shopify_json"), str):
                shopify_json = json.loads(article.get("shopify_json"))
            else:
                shopify_json = article.get("shopify_json")
        except:
            pass
    
    try:
        # Shopifyに投稿
        shopify_article_id = await publish_article_to_shopify(
            user_id=user_id,
            title=title,
            content=content,
            shopify_json=shopify_json
        )
        
        if shopify_article_id:
            # 記事を更新
            update_article(str(article_id), user_id, {
                "shopify_article_id": shopify_article_id,
                "status": "published"
            })
            
            # 履歴を記録
            create_article_history(
                article_id=str(article_id),
                action="published",
                changes={"shopify_article_id": shopify_article_id}
            )
            create_audit_log(
                user_id=user_id,
                action="article_published_shopify",
                metadata={"article_id": str(article_id), "shopify_article_id": shopify_article_id},
                ip_address=get_client_ip(request)
            )
            
            return {
                "message": "記事をShopifyに投稿しました",
                "shopify_article_id": shopify_article_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Shopifyへの投稿に失敗しました"
            )
    except ValueError as e:
        # Shopify設定が未完了
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shopify投稿エラー: {str(e)}"
        )


class KeywordSelection(BaseModel):
    selected_keywords: List[str]


@router.post(
    "/{article_id}/select-keywords",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60))]
)
async def select_keywords_endpoint(
    article_id: UUID,
    keyword_selection: KeywordSelection,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    ユーザーが選択したキーワードで記事生成を開始
    """
    from app.supabase_db import get_article_by_id
    from app.tasks import generate_article_task
    from fastapi import BackgroundTasks
    import json
    
    article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    if article.get("status") != "keyword_selection":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="キーワード選択のステータスではありません"
        )
    
    # 選択されたキーワードを保存
    analyzed_keywords_json = article.get("analyzed_keywords")
    if analyzed_keywords_json:
        if isinstance(analyzed_keywords_json, str):
            analyzed_keywords = json.loads(analyzed_keywords_json)
        else:
            analyzed_keywords = analyzed_keywords_json
        
        selected_keywords = keyword_selection.selected_keywords
        
        # 選択されたキーワードをフィルタリング
        selected_keywords_data = [
            kw for kw in analyzed_keywords 
            if kw.get("keyword") in selected_keywords
        ]
        
        # 記事データを取得（元の入力データ）
        article_data = {
            "keyword": article.get("keyword"),
            "target": article.get("target"),
            "article_type": article.get("article_type"),
            "important_keyword1": None,
            "important_keyword2": None,
            "important_keyword3": None,
            "secondary_keywords": selected_keywords  # 選択されたキーワードをセカンダリキーワードとして使用
        }
        
        # 選択されたキーワードを保存
        update_article(
            str(article_id),
            str(current_user.get("id")),
            {
                "status": "processing",
                "selected_keywords": json.dumps(selected_keywords, ensure_ascii=False),
                "selected_keywords_data": json.dumps(selected_keywords_data, ensure_ascii=False)
            }
        )
        
        # バックグラウンドで記事生成を開始
        from app.tasks import generate_article_task
        background_tasks.add_task(
            generate_article_task,
            article_id=str(article_id),
            article_data=article_data,
            user_id=str(current_user.get("id"))
        )
        
        return {
            "message": "キーワードを選択しました。記事生成を開始します。",
            "selected_keywords": selected_keywords,
            "selected_count": len(selected_keywords)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="キーワード分析データが見つかりません"
        )


@router.post(
    "/{article_id}/publish-wordpress",
    dependencies=[Depends(rate_limit(limit=10, window_seconds=300))]
)
async def publish_article_to_wordpress_endpoint(
    article_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """WordPressに記事を投稿（提供コードと同じ形式）"""
    import asyncio
    from app.wordpress_client import get_wordpress_config, publish_to_wordpress
    
    article = get_article_by_id(str(article_id), str(current_user.get("id")))
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="記事が見つかりません"
        )
    
    if not article.get("content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="記事内容が生成されていません"
        )
    
    user_id = str(current_user.get("id"))
    config = get_wordpress_config(user_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WordPress設定が完了していません。設定ページでWordPress情報を登録してください。"
        )
    
    title = article.get("title", "タイトルなし")
    content = article.get("content", "")
    
    # スラッグを生成（タイトルから）
    import re
    slug = None
    if title:
        slug = re.sub(r'[^\w\s-]', '', title).strip()
        slug = re.sub(r'[-\s]+', '-', slug)
    
    try:
        # 提供コードと同じ形式でWordPressに投稿（非同期で実行）
        res = await asyncio.to_thread(
            publish_to_wordpress,
            wp_url=config["url"],
            wp_user=config["user"],
            wp_pass=config["pass"],
            title=title,
            content=content,
            slug=slug,
            status="draft"
        )
        
        # レスポンスをチェック
        res.raise_for_status()
        
        # レスポンスから記事IDを取得
        result = res.json()
        wordpress_article_id = result.get("id")
        
        if wordpress_article_id:
            # 記事を更新（statusをpublishedに更新）
            update_article(
                article_id=str(article_id),
                user_id=user_id,
                updates={
                    "status": "published",
                }
            )
            
            # 履歴に記録
            create_article_history(
                article_id=str(article_id),
                action="published_wordpress",
                changes={"wordpress_article_id": wordpress_article_id}
            )
            create_audit_log(
                user_id=user_id,
                action="article_published_wordpress",
                metadata={"article_id": str(article_id), "wordpress_article_id": wordpress_article_id},
                ip_address=get_client_ip(request)
            )
            
            return {
                "message": "記事をWordPressに投稿しました",
                "wordpress_article_id": wordpress_article_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="WordPressへの投稿に失敗しました（記事IDが取得できませんでした）"
            )
    except requests.exceptions.HTTPError as e:
        error_detail = f"WordPress API エラー [{e.response.status_code}]: {e.response.text[:500]}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WordPress投稿エラー: {str(e)}"
        )
