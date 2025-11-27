"""
HTML sanitization helpers to mitigate XSS.
"""
from __future__ import annotations

from typing import Optional

import bleach

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "ul", "ol", "li", "blockquote",
    "code", "pre", "span", "a", "h1", "h2", "h3", "h4", "h5", "h6",
    "img"
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title"],
    "span": ["style"],
    "*": ["class"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(content: Optional[str]) -> Optional[str]:
    if content is None:
        return None
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
