#!/usr/bin/env python3
"""Verdis WebSocket Filter Proxy — filters unsafe RPC methods on WebSocket connections.

Sits between nginx and the Substrate node's WebSocket endpoint (port 9933),
filtering out the same unsafe methods as the HTTP RPC filter proxy.

Listens on 0.0.0.0:9944, forwards safe WebSocket requests to 127.0.0.1:9944.
"""
import asyncio
import json
import sys
import os
import time
import logging
from datetime import datetime

try:
    import websockets
except ImportError:
    print("websockets package not found. Install with: pip3 install websockets")
    sys.exit(1)

LISTEN_PORT = 9944
BACKEND_PORT = 9933
BACKEND_URL = f"ws://127.0.0.1:{BACKEND_PORT}"

# Same blocked methods as the HTTP RPC filter proxy
BLOCKED_METHODS = {
    "author_insertKey",
    "author_removeKey",
    "author_rotateKeys",
    "author_rotateKeysWithOwner",
    "author_pendingExtrinsics",
    "author_hasKey",
    "author_hasSessionKeys",
    "system_localListenAddresses",
    "system_localPeerId",
    "system_addReservedPeer",
    "system_removeReservedPeer",
    "system_setHeapPages",
    "system_setStorage",
    "system_addLog",
    "system_addWellKnownLog",
}

# author_submitExtrinsic IS needed for dapps to submit signed transactions
BLOCKED_METHODS.discard("author_submitExtrinsic")

LOG_FILE = "/var/log/verdis-ws-filter.log"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
    ]
)
logger = logging.getLogger("ws-filter")

request_count = 0
blocked_count = 0


def check_methods(data):
    """Check if a parsed JSON-RPC message contains blocked methods."""
    blocked = []

    # Single request
    if isinstance(data, dict) and "method" in data:
        method = data.get("method", "")
        if method in BLOCKED_METHODS:
            blocked.append(method)

    # Batch request
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "method" in item:
                method = item.get("method", "")
                if method in BLOCKED_METHODS:
                    blocked.append(method)

    return blocked


async def handle_client(client_ws, path=None):
    """Handle a WebSocket client connection, filtering blocked methods."""
    global request_count, blocked_count

    try:
        backend_ws = await websockets.connect(BACKEND_URL, max_size=10 * 1024 * 1024)
    except Exception as e:
        logger.error(f"Failed to connect to backend: {e}")
        await client_ws.close(code=1011, reason="Backend unavailable")
        return

    client_ip = "unknown"
    if hasattr(client_ws, 'remote_address'):
        client_ip = client_ws.remote_address[0] if client_ws.remote_address else "unknown"

    logger.info(f"Client connected from {client_ip}")

    async def client_to_backend():
        global request_count, blocked_count
        try:
            async for message in client_ws:
                request_count += 1
                try:
                    data = json.loads(message)
                    blocked = check_methods(data)

                    if blocked:
                        blocked_count += 1
                        logger.warning(f"BLOCKED from {client_ip}: {blocked}")

                        # Send error response(s) back to client
                        if isinstance(data, dict):
                            error_response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "error": {
                                    "code": -32601,
                                    "message": f"Method not allowed: {blocked[0]}"
                                }
                            }
                            await client_ws.send(json.dumps(error_response))
                        elif isinstance(data, list):
                            error_responses = []
                            for i, item in enumerate(data):
                                if isinstance(item, dict):
                                    error_responses.append({
                                        "jsonrpc": "2.0",
                                        "id": item.get("id"),
                                        "error": {
                                            "code": -32601,
                                            "message": f"Method not allowed: {blocked[i] if i < len(blocked) else 'unknown'}"
                                        }
                                    })
                                else:
                                    error_responses.append(item)
                            await client_ws.send(json.dumps(error_responses))
                        continue  # Don't forward blocked messages

                    # Forward safe messages to backend
                    await backend_ws.send(message)

                except json.JSONDecodeError:
                    # Not JSON — forward anyway (could be binary or non-RPC)
                    await backend_ws.send(message)

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"client_to_backend error: {e}")
        finally:
            await backend_ws.close()

    async def backend_to_client():
        try:
            async for message in backend_ws:
                await client_ws.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"backend_to_client error: {e}")

    # Run both directions concurrently
    await asyncio.gather(
        client_to_backend(),
        backend_to_client(),
        return_exceptions=True
    )

    logger.info(f"Client {client_ip} disconnected. Total: {request_count} reqs, {blocked_count} blocked")


async def main():
    logger.info(f"Verdis WebSocket Filter Proxy starting on 127.0.0.1:{LISTEN_PORT}")
    logger.info(f"Forwarding to {BACKEND_URL}")
    logger.info(f"Blocked methods: {BLOCKED_METHODS}")

    async with websockets.serve(handle_client, "0.0.0.0", LISTEN_PORT,
                                max_size=10 * 1024 * 1024,
                                ping_interval=30,
                                ping_timeout=120,
                                close_timeout=10):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
