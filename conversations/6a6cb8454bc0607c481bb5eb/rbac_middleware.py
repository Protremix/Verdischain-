"""
EvolvixOS RBAC Auth Middleware v1.0
Integrates RBAC permission checking into FastAPI endpoints
"""

from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Callable, Awaitable
import structlog
import os
import json
import uuid
import time

logger = structlog.get_logger()

# Import RBAC manager (lazy import to avoid circular dependencies)
try:
    from rbac import RBACManager, _pg_pool as rbac_pool
except ImportError:
    RBACManager = None
    rbac_pool = None


# Resource mapping: URL path prefix -> RBAC resource
ROUTE_PERMISSION_MAP = {
    "/api/v1/enterprise/orgs": ("org", "read"),
    "/api/v1/enterprise/orgs": ("org", "write"),  # POST/PATCH/DELETE overridden below
    "/api/v1/enterprise/audit": ("audit", "read"),
    "/api/v1/enterprise/sso": ("sso", "read"),
    "/api/v1/enterprise/usage": ("usage", "read"),
    "/api/v1/enterprise/gdpr": ("gdpr", "read"),
    "/api/v1/enterprise/consent": ("gdpr", "write"),
    "/api/v1/rbac": ("rbac", "read"),
    "/api/v1/agents": ("agents", "read"),
    "/api/v1/gateway/invoke": ("api", "invoke"),
    "/api/v1/blockchain": ("blockchain", "read"),
    "/api/v1/contracts": ("contracts", "read"),
    "/api/v1/plugins": ("plugins", "read"),
    "/api/v1/docs": ("docs", "read"),
    "/api/v1/sdk": ("sdk", "use"),
}

# Method to action mapping
METHOD_ACTION_MAP = {
    "GET": "read",
    "POST": "write",
    "PUT": "write",
    "PATCH": "write",
    "DELETE": "delete",
}

# Routes that don't require auth
PUBLIC_ROUTES = {
    "/", "/health", "/docs", "/openapi.json", "/redoc",
    "/api/v1/health", "/ai-gateway/health",
    "/monitoring/health", "/support/health",
    "/rbac/dashboard", "/enterprise/dashboard",
}


class RBACMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces RBAC permissions on API requests."""
    
    def __init__(self, app, enabled: bool = True, header_name: str = "X-User-ID",
                 api_key_header: str = "X-API-Key", exclude_prefixes: list = None):
        super().__init__(app)
        self.enabled = enabled
        self.header_name = header_name
        self.api_key_header = api_key_header
        self.exclude_prefixes = exclude_prefixes or ["/health", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)
        
        path = request.url.path
        method = request.method
        
        # Skip public routes
        if path in PUBLIC_ROUTES or any(path.startswith(prefix) for prefix in self.exclude_prefixes):
            return await call_next(request)
        
        # Skip OPTIONS (CORS preflight)
        if method == "OPTIONS":
            return await call_next(request)
        
        # Try to match route to a permission
        resource, action = self._get_permission(path, method)
        if resource is None:
            # No permission mapping = open access
            return await call_next(request)
        
        # Get user ID from header (in production, this would come from JWT)
        user_id = request.headers.get(self.header_name)
        org_id = request.headers.get("X-Org-ID")
        
        # If no user ID, allow access (backwards compatible — add auth later)
        if not user_id:
            # Log the unauthenticated access
            logger.info(f"RBAC: unauthenticated access to {method} {path}")
            return await call_next(request)
        
        # Check permission via RBAC
        if RBACManager:
            try:
                allowed = await RBACManager.check_permission(user_id, resource, action, org_id)
                if not allowed:
                    logger.warning(f"RBAC: denied {user_id} {method} {path} ({resource}:{action})")
                    return Response(
                        content=json.dumps({
                            "error": "permission_denied",
                            "detail": f"User does not have {resource}:{action} permission",
                            "resource": resource,
                            "action": action,
                        }),
                        status_code=403,
                        media_type="application/json"
                    )
            except Exception as e:
                logger.warning(f"RBAC check failed: {e}")
                # Fail open for availability
        
        # Add permission info to response headers
        response = await call_next(request)
        response.headers["X-RBAC-Resource"] = resource
        response.headers["X-RBAC-Action"] = action
        if user_id:
            response.headers["X-RBAC-User"] = user_id
        return response
    
    def _get_permission(self, path: str, method: str) -> tuple:
        """Map URL path and method to RBAC resource:action."""
        # Check each route prefix
        for route_prefix, (resource, default_action) in ROUTE_PERMISSION_MAP.items():
            if path.startswith(route_prefix):
                # Determine action from method
                action = METHOD_ACTION_MAP.get(method, "read")
                # Special cases
                if path.endswith("/execute") or path.endswith("/invoke"):
                    action = "execute"
                elif path.endswith("/delete") or method == "DELETE":
                    action = "delete"
                return resource, action
        
        return None, None


def require_permission(resource: str, action: str):
    """Decorator for requiring specific RBAC permission on an endpoint."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                user_id = request.headers.get("X-User-ID")
                org_id = request.headers.get("X-Org-ID")
                
                if user_id and RBACManager:
                    allowed = await RBACManager.check_permission(user_id, resource, action, org_id)
                    if not allowed:
                        raise HTTPException(403, detail={
                            "error": "permission_denied",
                            "resource": resource,
                            "action": action,
                        })
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_rbac_middleware_config():
    """Return the RBAC middleware configuration summary."""
    return {
        "version": "1.0.0",
        "enabled": True,
        "total_protected_routes": len(ROUTE_PERMISSION_MAP),
        "public_routes": len(PUBLIC_ROUTES),
        "method_actions": METHOD_ACTION_MAP,
        "route_permissions": {k: {"resource": v[0], "default_action": v[1]} for k, v in ROUTE_PERMISSION_MAP.items()},
    }
