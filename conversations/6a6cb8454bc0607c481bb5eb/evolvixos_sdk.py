"""
EvolvixOS Developer SDK — Python
Unified SDK for AI Gateway, Agent Framework, and Blockchain interactions

Usage:
    from evolvixos_sdk import EvolvixOSClient
    
    client = EvolvixOSClient(base_url="https://evolvixos.com", api_key="evk_...")
    
    # AI Gateway
    result = await client.gateway.invoke("sentiment", {"text": "Hello!"})
    
    # Agent Framework
    agent = client.agents.create(name="My Agent", capabilities=["chat"])
    client.agents.start(agent.id)
    task = client.agents.create_task(agent.id, "chat", {"text": "Hi"})
    result = await client.agents.execute_task(agent.id, task.id)
    
    # Memory
    client.memory.store(agent.id, "key", "value")
    value = client.memory.get(agent.id, "key")
    
    # Blockchain
    block = client.blockchain.get_block(123)
    pools = client.blockchain.get_dex_pools()
"""

import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# =========================================================================
# Base Client
# =========================================================================

class EvolvixOSClient:
    """Main SDK client for EvolvixOS platform"""
    
    def __init__(self, base_url: str = "https://evolvixos.com", api_key: str = None,
                 agent_url: str = None, gateway_url: str = None, blockchain_url: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._gateway_url = gateway_url or f"{self.base_url}/ai-gateway"
        self._agent_url = agent_url or f"{self.base_url}/agents"
        self._blockchain_url = blockchain_url or f"{self.base_url}/blockchain/api"
        
        self.gateway = GatewayClient(self._gateway_url, api_key)
        self.agents = AgentClient(self._agent_url, api_key)
        self.memory = MemoryClient(self._agent_url, api_key)
        self.blockchain = BlockchainClient(self._blockchain_url, api_key)
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

# =========================================================================
# AI Gateway Client
# =========================================================================

class GatewayClient:
    """Client for AI Gateway operations"""
    
    def __init__(self, url: str, api_key: str = None):
        self.url = url.rstrip("/")
        self.api_key = api_key
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def invoke(self, capability: str, input_data: Dict,
                     plugin: str = None, max_tokens: int = None,
                     timeout: int = None) -> Dict:
        """Invoke an AI capability"""
        options = {"capability": capability}
        if max_tokens:
            options["max_tokens"] = max_tokens
        if timeout:
            options["timeout"] = timeout
        
        payload = {
            "capability": capability,
            "input": input_data,
            "options": options,
        }
        if plugin:
            payload["plugin"] = plugin
        
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.url}/gateway/invoke",
                json=payload,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()
    
    async def chat(self, messages: List[Dict], model: str = None, max_tokens: int = 4096) -> Dict:
        """Chat completion"""
        input_data = {"messages": messages}
        if model:
            input_data["model"] = model
        return await self.invoke("chat", input_data, max_tokens=max_tokens)
    
    async def sentiment(self, text: str) -> Dict:
        """Analyze sentiment"""
        return await self.invoke("sentiment", {"text": text})
    
    async def code_review(self, code: str, language: str = "python") -> Dict:
        """Review code"""
        return await self.invoke("code_review", {"code": code, "language": language})
    
    async def completion(self, prompt: str, max_tokens: int = 100) -> Dict:
        """Text completion"""
        return await self.invoke("completion", {"prompt": prompt, "max_tokens": max_tokens})
    
    async def embedding(self, text: str) -> Dict:
        """Generate embedding"""
        return await self.invoke("embedding", {"text": text})
    
    async def health(self) -> Dict:
        """Check gateway health"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/health")
            return resp.json()
    
    async def list_plugins(self) -> Dict:
        """List available plugins"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/plugins", headers=self._headers())
            return resp.json()
    
    async def get_stats(self) -> Dict:
        """Get gateway statistics"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/gateway/stats", headers=self._headers())
            return resp.json()
    
    async def list_capabilities(self) -> Dict:
        """List available capabilities"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/capabilities", headers=self._headers())
            return resp.json()
    
    async def clear_cache(self) -> Dict:
        """Clear gateway cache"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/cache/clear", headers=self._headers())
            return resp.json()

# =========================================================================
# Agent Client
# =========================================================================

class AgentClient:
    """Client for Agent Framework operations"""
    
    def __init__(self, url: str, api_key: str = None):
        self.url = url.rstrip("/")
        self.api_key = api_key
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def create(self, name: str, description: str = "",
                     capabilities: List[str] = None,
                     system_prompt: str = "", model: str = "gpt-4o",
                     config: Dict = None, tags: List[str] = None) -> Dict:
        """Create a new agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents", json={
                "name": name,
                "description": description,
                "capabilities": capabilities or ["chat"],
                "system_prompt": system_prompt,
                "model": model,
                "config": config or {},
                "tags": tags or [],
            }, headers=self._headers())
            return resp.json()
    
    async def list(self, status: str = None) -> Dict:
        """List agents"""
        params = {"status": status} if status else {}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents", params=params, headers=self._headers())
            return resp.json()
    
    async def get(self, agent_id: str) -> Dict:
        """Get agent by ID"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}", headers=self._headers())
            return resp.json()
    
    async def update(self, agent_id: str, **kwargs) -> Dict:
        """Update agent"""
        data = {k: v for k, v in kwargs.items() if v is not None}
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{self.url}/agents/{agent_id}", json=data, headers=self._headers())
            return resp.json()
    
    async def delete(self, agent_id: str) -> Dict:
        """Delete agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.url}/agents/{agent_id}", headers=self._headers())
            return resp.json()
    
    async def start(self, agent_id: str) -> Dict:
        """Start agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/start", headers=self._headers())
            return resp.json()
    
    async def pause(self, agent_id: str) -> Dict:
        """Pause agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/pause", headers=self._headers())
            return resp.json()
    
    async def stop(self, agent_id: str) -> Dict:
        """Stop agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/stop", headers=self._headers())
            return resp.json()
    
    async def stats(self, agent_id: str) -> Dict:
        """Get agent statistics"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}/stats", headers=self._headers())
            return resp.json()
    
    async def create_task(self, agent_id: str, task_type: str,
                          input_data: Dict, priority: int = 2,
                          timeout: int = 120) -> Dict:
        """Create a task for an agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/tasks", json={
                "task_type": task_type,
                "input_data": input_data,
                "priority": priority,
                "timeout": timeout,
            }, headers=self._headers())
            return resp.json()
    
    async def execute_task(self, agent_id: str, task_id: str) -> Dict:
        """Execute a task"""
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/tasks/{task_id}/execute", headers=self._headers())
            return resp.json()
    
    async def list_tasks(self, agent_id: str = None, status: str = None, limit: int = 50) -> Dict:
        """List tasks"""
        params = {}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        params["limit"] = limit
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/tasks", params=params, headers=self._headers())
            return resp.json()
    
    async def get_task(self, task_id: str) -> Dict:
        """Get task by ID"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/tasks/{task_id}", headers=self._headers())
            return resp.json()
    
    async def cancel_task(self, task_id: str) -> Dict:
        """Cancel a task"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/tasks/{task_id}/cancel", headers=self._headers())
            return resp.json()
    
    async def framework_stats(self) -> Dict:
        """Get framework statistics"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/stats", headers=self._headers())
            return resp.json()

# =========================================================================
# Memory Client
# =========================================================================

class MemoryClient:
    """Client for agent memory operations"""
    
    def __init__(self, url: str, api_key: str = None):
        self.url = url.rstrip("/")
        self.api_key = api_key
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def store(self, agent_id: str, key: str, value: Any,
                    memory_type: str = "long_term",
                    context: Dict = None, importance: float = 0.5,
                    ttl_seconds: int = None) -> Dict:
        """Store a memory entry"""
        data = {
            "key": key,
            "value": value,
            "memory_type": memory_type,
            "importance": importance,
        }
        if context:
            data["context"] = context
        if ttl_seconds:
            data["ttl_seconds"] = ttl_seconds
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.url}/agents/{agent_id}/memory", json=data, headers=self._headers())
            return resp.json()
    
    async def get(self, agent_id: str, key: str) -> Dict:
        """Retrieve a memory entry"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}/memory/{key}", headers=self._headers())
            return resp.json()
    
    async def list(self, agent_id: str, memory_type: str = None) -> Dict:
        """List memories for an agent"""
        params = {}
        if memory_type:
            params["memory_type"] = memory_type
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}/memory", params=params, headers=self._headers())
            return resp.json()
    
    async def update(self, agent_id: str, key: str, value: Any,
                     importance: float = None) -> Dict:
        """Update a memory entry"""
        data = {"value": value}
        if importance is not None:
            data["importance"] = importance
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{self.url}/agents/{agent_id}/memory/{key}", json=data, headers=self._headers())
            return resp.json()
    
    async def delete(self, agent_id: str, key: str) -> Dict:
        """Delete a memory entry"""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.url}/agents/{agent_id}/memory/{key}", headers=self._headers())
            return resp.json()
    
    async def search(self, agent_id: str, query: str, limit: int = 10) -> Dict:
        """Search agent memories"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}/memory/search/{query}",
                                   params={"limit": limit}, headers=self._headers())
            return resp.json()
    
    async def stats(self, agent_id: str) -> Dict:
        """Get memory statistics"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/agents/{agent_id}/memory/stats", headers=self._headers())
            return resp.json()
    
    async def clear(self, agent_id: str) -> Dict:
        """Clear all memories for an agent"""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.url}/agents/{agent_id}/memory", headers=self._headers())
            return resp.json()

# =========================================================================
# Blockchain Client
# =========================================================================

class BlockchainClient:
    """Client for Verdis blockchain operations"""
    
    def __init__(self, url: str, api_key: str = None):
        self.url = url.rstrip("/")
        self.api_key = api_key
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def get_block(self, height: int) -> Dict:
        """Get block by height"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/blocks/{height}", headers=self._headers())
            return resp.json()
    
    async def get_latest_block(self) -> Dict:
        """Get latest block"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/blocks/latest", headers=self._headers())
            return resp.json()
    
    async def get_validators(self) -> Dict:
        """Get validator list"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/validators", headers=self._headers())
            return resp.json()
    
    async def get_dex_pools(self) -> Dict:
        """Get DEX pools"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/dex/pools", headers=self._headers())
            return resp.json()
    
    async def get_chain_state(self) -> Dict:
        """Get chain state"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/chain-state", headers=self._headers())
            return resp.json()
    
    async def get_tokenomics(self) -> Dict:
        """Get tokenomics data"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/tokenomics", headers=self._headers())
            return resp.json()
    
    async def get_eco_stats(self) -> Dict:
        """Get eco/carbon credit stats"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.url}/eco/stats", headers=self._headers())
            return resp.json()
