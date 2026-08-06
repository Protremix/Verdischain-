"""
EvolvixOS AI Gateway — Security Integration Patch
Adds API key auth, security headers, input validation, and graceful shutdown to the gateway

This file patches ai_gateway.py to integrate gateway_security.py
"""

import os
import json
import sys

# Read the current ai_gateway.py
gateway_path = os.getenv("GATEWAY_PATH", "/opt/evolvixos/ai-gateway/ai_gateway.py")
with open(gateway_path) as f:
    content = f.read()

# 1. Add security imports
security_import = """
# =========================================================================
# Security Integration (Phase 90)
# =========================================================================
from gateway_security import (
    APIKeyManager, RedisState, DistributedRateLimiter,
    GracefulShutdownManager, SecurityHeaders, InputValidator,
)

# Initialize security components
api_key_manager = APIKeyManager()
redis_state = RedisState(os.getenv("REDIS_URL", "redis://localhost:6379/2"))
distributed_rate_limiter = DistributedRateLimiter(redis_state)
shutdown_manager = GracefulShutdownManager()

# Create a default API key on first startup
def ensure_default_api_key():
    \"\"\"Create a default API key if none exist\"\"\"
    if not api_key_manager.keys:
        result = api_key_manager.create_key(
            name="default",
            scopes=["*"],
            rate_limit=100,
        )
        print(f"Created default API key: {result['api_key']}")
        return result
    return None
"""

# Insert after the existing imports (after the line "logger = structlog.get_logger()")
marker = "logger = structlog.get_logger()"
if marker in content and "APIKeyManager" not in content:
    content = content.replace(marker, marker + "\n" + security_import)
    print("Added security imports")

# 2. Add security headers middleware
security_middleware = """
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    for key, value in SecurityHeaders.get_headers().items():
        response.headers[key] = value
    return response

# =========================================================================
# Authentication Dependency
# =========================================================================

async def require_api_key(request: Request):
    \"\"\"Dependency that validates API key from header or query param\"\"\"
    # Skip auth for health and docs endpoints
    if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
        return None
    
    # Get API key from header or query
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required. Provide via X-API-Key header or api_key query param.")
    
    key = api_key_manager.validate_key(api_key)
    if not key:
        raise HTTPException(status_code=403, detail="Invalid or revoked API key.")
    
    # Check rate limit
    if not distributed_rate_limiter.check_api_key(key.key_id, key.rate_limit_per_min):
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({key.rate_limit_per_min}/min)")
    
    return key

async def optional_api_key(request: Request):
    \"\"\"Optional API key - doesn't fail if missing, but validates if present\"\"\"
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    if api_key:
        return api_key_manager.validate_key(api_key)
    return None
"""

# Insert before the first endpoint
marker2 = '@app.get("/health")'
if marker2 in content and "require_api_key" not in content:
    content = content.replace(marker2, security_middleware + "\n" + marker2)
    print("Added security middleware and auth dependency")

# 3. Add API key management endpoints
api_key_endpoints = """
# =========================================================================
# API Key Management Endpoints
# =========================================================================

@app.post("/api-keys/create")
async def create_api_key(name: str, scopes: str = "*", rate_limit: int = 60):
    \"\"\"Create a new API key. Scopes: comma-separated list or * for all.\"\"\"
    scope_list = scopes.split(",") if scopes != "*" else ["*"]
    result = api_key_manager.create_key(name, scope_list, rate_limit)
    return result

@app.get("/api-keys")
async def list_api_keys():
    \"\"\"List all API keys (without raw keys)\"\"\"
    return {"keys": api_key_manager.list_keys()}

@app.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    \"\"\"Revoke an API key\"\"\"
    success = api_key_manager.revoke_key(key_id)
    return {"success": success, "key_id": key_id}

@app.get("/api-keys/{key_id}/usage")
async def api_key_usage(key_id: str):
    \"\"\"Get API key usage statistics\"\"\"
    if key_id not in api_key_manager.keys:
        raise HTTPException(status_code=404, detail="API key not found")
    key = api_key_manager.keys[key_id]
    return {
        "key_id": key.key_id,
        "name": key.name,
        "scopes": key.scopes,
        "rate_limit_per_min": key.rate_limit_per_min,
        "request_count": key.request_count,
        "last_used": key.last_used,
        "active": key.active,
    }
"""

# Insert before the startup event
marker3 = '@app.on_event("startup")'
if marker3 in content and "api-keys/create" not in content:
    content = content.replace(marker3, api_key_endpoints + "\n" + marker3)
    print("Added API key endpoints")

# 4. Add input validation to invoke endpoint
# Replace the invoke endpoint to add validation
old_invoke_start = '''@app.post("/gateway/invoke")
async def invoke_gateway(request: GatewayRequest, http_request: Request):
    """Main gateway endpoint — routes request to the best plugin"
    # Rate limiting
    client_id = http_request.client.host if http_request.client else "unknown"
    if not rate_limiter.check(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")'''

new_invoke_start = '''@app.post("/gateway/invoke")
async def invoke_gateway(request: GatewayRequest, http_request: Request, api_key = Depends(optional_api_key)):
    """Main gateway endpoint — routes request to the best plugin"""
    # Validate input
    try:
        InputValidator.validate_input(request.input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # API key rate limiting (if key provided)
    if api_key:
        if not distributed_rate_limiter.check_api_key(api_key.key_id, api_key.rate_limit_per_min):
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({api_key.rate_limit_per_min}/min)")
        # Check scope
        if not api_key_manager.check_scope(api_key, request.capability):
            raise HTTPException(status_code=403, detail=f"API key does not have access to capability: {request.capability}")
    
    # Standard rate limiting
    client_id = http_request.client.host if http_request.client else "unknown"
    if not rate_limiter.check(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")'''

if old_invoke_start in content:
    content = content.replace(old_invoke_start, new_invoke_start)
    print("Updated invoke endpoint with validation and auth")

# 5. Add graceful shutdown to unload_plugin endpoint
old_unload = '''@app.post("/plugins/{name}/unload")
async def unload_plugin(name: str):
    success = plugin_manager.unload_plugin(name)
    return {"success": success, "name": name}'''

new_unload = '''@app.post("/plugins/{name}/unload")
async def unload_plugin(name: str):
    # Signal graceful shutdown - block new requests
    shutdown_manager.signal_shutdown(name)
    # Wait for in-flight requests to complete
    await shutdown_manager.wait_for_idle(name, timeout=10.0)
    success = plugin_manager.unload_plugin(name)
    return {"success": success, "name": name}'''

if old_unload in content:
    content = content.replace(old_unload, new_unload)
    print("Added graceful shutdown to unload endpoint")

# 6. Add shutdown tracking to invoke endpoint
# Add request tracking around plugin execution
old_execute = '''        # Execute plugin
        plugin = plugin_manager.get_plugin(plugin_name)'''

new_execute = '''        # Graceful shutdown check
        if not shutdown_manager.start_request(plugin_name, request.request_id):
            raise HTTPException(status_code=503, detail=f"Plugin {plugin_name} is shutting down")
        
        # Execute plugin
        plugin = plugin_manager.get_plugin(plugin_name)'''

if old_execute in content and "shutdown_manager.start_request" not in content:
    content = content.replace(old_execute, new_execute)
    print("Added shutdown tracking to invoke")

# Add end_request after execution
old_finally = '''    except HTTPException:
        router.release_load(plugin_name)
        raise
    except Exception as e:
        router.release_load(plugin_name)'''

new_finally = '''    except HTTPException:
        router.release_load(plugin_name)
        shutdown_manager.end_request(plugin_name, request.request_id)
        raise
    except Exception as e:
        router.release_load(plugin_name)
        shutdown_manager.end_request(plugin_name, request.request_id)'''

if old_finally in content and "shutdown_manager.end_request" not in content:
    content = content.replace(old_finally, new_finally)
    print("Added end_request to error handlers")

# Also add end_request on success (before the return)
old_success_return = '''        router.release_load(plugin_name)
        
        return GatewayResponse('''
new_success_return = '''        router.release_load(plugin_name)
        shutdown_manager.end_request(plugin_name, request.request_id)
        
        return GatewayResponse('''

if old_success_return in content and "shutdown_manager.end_request" not in content.replace("shutdown_manager.end_request(plugin_name, request.request_id)\n        raise", ""):
    content = content.replace(old_success_return, new_success_return)
    print("Added end_request on success")

# 7. Add startup hook to create default API key
old_startup = '''    logger.info(f"Gateway ready with {len(plugin_manager.instances)} active plugins")'''

new_startup = '''    # Create default API key if none exist
    ensure_default_api_key()
    
    logger.info(f"Gateway ready with {len(plugin_manager.instances)} active plugins")'''

if old_startup in content and "ensure_default_api_key()" not in content:
    content = content.replace(old_startup, new_startup)
    print("Added default API key creation to startup")

# Write the updated file
with open(gateway_path, 'w') as f:
    f.write(content)

print(f"\nSecurity integration complete. File: {gateway_path}")
print("Verify with: python3 -c 'import py_compile; py_compile.compile(\"" + gateway_path + "\")'")
