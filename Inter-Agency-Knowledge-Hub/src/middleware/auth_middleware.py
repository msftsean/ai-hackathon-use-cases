"""Authentication middleware for Inter-Agency Knowledge Hub."""

import logging
from functools import wraps
from typing import Callable, Optional

from flask import request, g, jsonify

from ..core.auth import get_authenticator
from ..models.user import UserPermissions

logger = logging.getLogger("knowledge_hub")


def get_token_from_request() -> Optional[str]:
    """Extract bearer token from request headers."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


async def validate_and_get_permissions(token: str) -> Optional[UserPermissions]:
    """Validate token and get user permissions."""
    authenticator = get_authenticator()
    return await authenticator.get_user_permissions(token)


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({"error": "Authorization token required"}), 401

        permissions = await validate_and_get_permissions(token)
        if not permissions:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Store permissions in request context
        g.permissions = permissions
        g.user_id = permissions.user_id
        g.ip_address = request.remote_addr or ""
        g.session_id = request.headers.get("X-Session-ID", "")

        return await f(*args, **kwargs)

    return decorated


def require_admin(f: Callable) -> Callable:
    """Decorator to require admin privileges."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        # First check authentication
        token = get_token_from_request()

        if not token:
            return jsonify({"error": "Authorization token required"}), 401

        permissions = await validate_and_get_permissions(token)
        if not permissions:
            return jsonify({"error": "Invalid or expired token"}), 401

        if not permissions.is_admin:
            logger.warning(f"Non-admin user {permissions.user_id} attempted admin action")
            return jsonify({"error": "Admin privileges required"}), 403

        g.permissions = permissions
        g.user_id = permissions.user_id
        g.ip_address = request.remote_addr or ""
        g.session_id = request.headers.get("X-Session-ID", "")

        return await f(*args, **kwargs)

    return decorated


def require_reviewer(f: Callable) -> Callable:
    """Decorator to require reviewer privileges."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({"error": "Authorization token required"}), 401

        permissions = await validate_and_get_permissions(token)
        if not permissions:
            return jsonify({"error": "Invalid or expired token"}), 401

        if not permissions.is_reviewer and not permissions.is_admin:
            logger.warning(f"Non-reviewer user {permissions.user_id} attempted reviewer action")
            return jsonify({"error": "Reviewer privileges required"}), 403

        g.permissions = permissions
        g.user_id = permissions.user_id
        g.ip_address = request.remote_addr or ""
        g.session_id = request.headers.get("X-Session-ID", "")

        return await f(*args, **kwargs)

    return decorated


def optional_auth(f: Callable) -> Callable:
    """Decorator for routes where authentication is optional."""
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = get_token_from_request()

        if token:
            permissions = await validate_and_get_permissions(token)
            if permissions:
                g.permissions = permissions
                g.user_id = permissions.user_id
            else:
                g.permissions = None
                g.user_id = None
        else:
            g.permissions = None
            g.user_id = None

        g.ip_address = request.remote_addr or ""
        g.session_id = request.headers.get("X-Session-ID", "")

        return await f(*args, **kwargs)

    return decorated
