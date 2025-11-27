"""
構造化データ（Schema.org）の自動生成
"""
from typing import Dict, Optional
from datetime import datetime


def generate_article_schema(
    title: str,
    content: str,
    author: str = "eightoon",
    published_date: Optional[str] = None,
    modified_date: Optional[str] = None,
    url: Optional[str] = None,
    image_url: Optional[str] = None
) -> Dict:
    """
    Article Schema（記事の構造化データ）を生成
    
    Args:
        title: 記事タイトル
        content: 記事本文
        author: 著者名
        published_date: 公開日（ISO 8601形式）
        modified_date: 更新日（ISO 8601形式）
        url: 記事URL
        image_url: 記事画像URL
    
    Returns:
        JSON-LD形式の構造化データ
    """
    if not published_date:
        published_date = datetime.now().isoformat()
    if not modified_date:
        modified_date = published_date
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "author": {
            "@type": "Person",
            "name": author
        },
        "datePublished": published_date,
        "dateModified": modified_date,
        "articleBody": content[:500]  # 最初の500文字
    }
    
    if url:
        schema["url"] = url
    
    if image_url:
        schema["image"] = image_url
    
    return schema


def generate_faq_schema(faq_items: list) -> Optional[Dict]:
    """
    FAQPage Schema（FAQセクションの構造化データ）を生成
    
    Args:
        faq_items: FAQのリスト（質問と回答の辞書のリスト、または質問のみのリスト）
    
    Returns:
        JSON-LD形式のFAQ構造化データ
    """
    if not faq_items or len(faq_items) == 0:
        return None
    
    # faq_itemsが辞書のリストの場合
    if isinstance(faq_items[0], dict):
        questions = [item.get("question", "") for item in faq_items if item.get("question")]
        answers = [item.get("answer", "") for item in faq_items if item.get("answer")]
    else:
        # 質問のみのリストの場合、回答は空文字列
        questions = faq_items
        answers = [""] * len(questions)
    
    if not questions:
        return None
    
    main_entity = []
    for q, a in zip(questions, answers):
        main_entity.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a if a else "この質問への回答は記事本文をご確認ください。"
            }
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity
    }


def generate_breadcrumb_schema(breadcrumbs: list) -> Optional[Dict]:
    """
    BreadcrumbList Schema（パンくずリストの構造化データ）を生成
    
    Args:
        breadcrumbs: パンくずのリスト（{"name": "ホーム", "url": "/"}の形式）
    
    Returns:
        JSON-LD形式のパンくず構造化データ
    """
    if not breadcrumbs or len(breadcrumbs) == 0:
        return None
    
    item_list_element = []
    for i, crumb in enumerate(breadcrumbs, 1):
        item_list_element.append({
            "@type": "ListItem",
            "position": i,
            "name": crumb.get("name", ""),
            "item": crumb.get("url", "")
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list_element
    }


def generate_organization_schema(
    name: str = "EIGHTOON",
    url: str = "https://eightoon.com",
    logo_url: Optional[str] = None
) -> Dict:
    """
    Organization Schema（組織情報の構造化データ）を生成
    
    Args:
        name: 組織名
        url: 組織URL
        logo_url: ロゴURL
    
    Returns:
        JSON-LD形式の組織構造化データ
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url
    }
    
    if logo_url:
        schema["logo"] = logo_url
    
    return schema


def generate_all_schemas(
    title: str,
    content: str,
    faq_items: Optional[list] = None,
    breadcrumbs: Optional[list] = None,
    author: str = "eightoon",
    url: Optional[str] = None,
    image_url: Optional[str] = None
) -> Dict[str, Dict]:
    """
    全ての構造化データを生成
    
    Returns:
        構造化データの辞書（キー: schema_type, 値: 構造化データ）
    """
    schemas = {}
    
    # Article Schema
    schemas["article"] = generate_article_schema(
        title=title,
        content=content,
        author=author,
        url=url,
        image_url=image_url
    )
    
    # FAQPage Schema
    if faq_items:
        faq_schema = generate_faq_schema(faq_items)
        if faq_schema:
            schemas["faq"] = faq_schema
    
    # BreadcrumbList Schema
    if breadcrumbs:
        breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)
        if breadcrumb_schema:
            schemas["breadcrumb"] = breadcrumb_schema
    
    # Organization Schema
    schemas["organization"] = generate_organization_schema()
    
    return schemas

