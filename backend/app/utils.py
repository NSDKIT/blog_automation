from typing import Optional

from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP (best-effort) from the FastAPI request."""
    if request.client:
        return request.client.host
    return None
