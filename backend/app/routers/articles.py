from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from uuid import UUID
from app.supabase_db import (
    get_articles_by_user_id, get_article_by_id, create_article,
    update_article, delete_article, create_article_history
)
from app.schemas import ArticleCreate, ArticleResponse, ArticleUpdate
from app.dependencies import get_current_user
from app.tasks import generate_article_task

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


@router.post("", response_model=ArticleResponse)
async def create_article_endpoint(
    article_data: ArticleCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    # 記事レコードを作成
    article = create_article(
        user_id=str(current_user.get("id")),
        keyword=article_data.keyword,
        target=article_data.target,
        article_type=article_data.article_type,
        status="processing"
    )
    
    # 履歴を記録
    create_article_history(
        article_id=article.get("id"),
        action="created",
        changes={"keyword": article_data.keyword, "target": article_data.target}
    )
    
    # バックグラウンドで記事生成を開始
    background_tasks.add_task(
        generate_article_task,
        article_id=article.get("id"),
        article_data=article_data.dict(),
        user_id=str(current_user.get("id"))
    )
    
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article_endpoint(
    article_id: UUID,
    article_update: ArticleUpdate,
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
        changes["content"] = {"old": existing_article.get("content"), "new": article_update.content}
        updates["content"] = article_update.content
    
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
    
    return article


@router.delete("/{article_id}")
async def delete_article_endpoint(
    article_id: UUID,
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
    
    return {"message": "記事を削除しました"}


@router.post("/{article_id}/publish")
async def publish_article_endpoint(
    article_id: UUID,
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


@router.post("/{article_id}/publish-wordpress")
async def publish_article_to_wordpress_endpoint(
    article_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """WordPressに記事を投稿"""
    from app.wordpress_client import (
        publish_article_to_wordpress, 
        upload_image_to_wordpress,
        WordPressError
    )
    import re
    import os
    
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
    
    try:
        # コンテンツから画像URLを抽出
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        img_urls = re.findall(img_pattern, content)
        
        # 最初の画像をサムネイルとして使用
        featured_media_id = None
        if img_urls:
            try:
                first_image_url = img_urls[0]
                image_filename = os.path.basename(first_image_url.split('?')[0]) or "image.jpg"
                featured_media_id = await upload_image_to_wordpress(
                    user_id=user_id,
                    image_url=first_image_url,
                    image_filename=image_filename
                )
            except WordPressError as e:
                # 画像アップロードエラーは警告として記録するが、記事投稿は続行
                print(f"画像アップロードエラー（スキップ）: {e}")
            except Exception as e:
                # その他のエラーも警告として記録
                print(f"画像アップロードエラー（スキップ）: {str(e)}")
        
        # スラッグを生成（タイトルから）
        slug = None
        if title:
            import unicodedata
            # 日本語をローマ字に変換する代わりに、タイトルをそのまま使用
            # 実際の実装では、より適切なスラッグ生成が必要かもしれません
            slug = re.sub(r'[^\w\s-]', '', title).strip()
            slug = re.sub(r'[-\s]+', '-', slug)
        
        # WordPressに投稿
        wordpress_article_id = await publish_article_to_wordpress(
            user_id=user_id,
            title=title,
            content=content,
            slug=slug,
            featured_media_id=featured_media_id,
            status="publish",
            comment_status="closed"
        )
        
        if wordpress_article_id:
            # 記事を更新（wordpress_article_idを保存するカラムが必要）
            # 現在はshopify_article_idしかないので、settingsテーブルに保存するか、
            # articlesテーブルにwordpress_article_idカラムを追加する必要があります
            # ここでは一旦、履歴に記録するだけにします
            create_article_history(
                article_id=str(article_id),
                action="published_wordpress",
                changes={"wordpress_article_id": wordpress_article_id}
            )
            
            return {
                "message": "記事をWordPressに投稿しました",
                "wordpress_article_id": wordpress_article_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="WordPressへの投稿に失敗しました"
            )
    except ValueError as e:
        # WordPress設定が未完了
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except WordPressError as e:
        # WordPress.com APIエラー
        error_detail = f"WordPress.com API エラー [{e.status_code}]: {e.message}"
        if e.status_code == 403:
            error_detail += (
                "\n\n認証エラーの可能性があります。以下を確認してください:\n"
                "1. WordPress.comのユーザー名（メールアドレス）が正しいか確認してください\n"
                "2. アプリケーションパスワードが正しく発行されているか確認してください\n"
                "3. アプリケーションパスワードにスペースが含まれている場合は、そのまま入力してください（例: xxxx xxxx xxxx xxxx）\n"
                "4. WordPress.comのセキュリティ設定（https://wordpress.com/me/security）でアプリケーションパスワードが有効か確認してください\n"
                "5. サイトURLが正しいか確認してください（例: https://example.wordpress.com）\n"
                "6. アプリケーションパスワードが取り消されていないか確認してください"
            )
        elif e.status_code == 404:
            error_detail += (
                "\n\n確認事項:\n"
                "1. WordPress.comサイトURLが正しいか確認してください（例: https://example.wordpress.com）\n"
                "2. サイトが存在するか確認してください\n"
                "3. サイトURLに末尾のスラッシュ（/）が含まれていないか確認してください"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WordPress投稿エラー: {str(e)}"
        )

