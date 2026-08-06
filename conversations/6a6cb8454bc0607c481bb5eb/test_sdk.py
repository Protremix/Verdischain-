"""
EvolvixOS SDK — Test Suite
Tests the Python SDK against live endpoints
"""

import pytest
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolvixos_sdk import EvolvixOSClient, GatewayClient, AgentClient, MemoryClient, BlockchainClient

# Use local URLs for testing
BASE_URL = "http://localhost:3500"
AGENT_URL = "http://localhost:3600"
BLOCKCHAIN_URL = "http://localhost:3200"

# =========================================================================
# Gateway Client Tests (mocked)
# =========================================================================

class TestGatewayClient:
    def setup_method(self):
        self.client = GatewayClient(BASE_URL, api_key=None)

    def test_init(self):
        assert self.client.url == BASE_URL
        assert self.client.api_key is None

    def test_init_with_api_key(self):
        c = GatewayClient(BASE_URL, api_key="evk_test")
        assert c.api_key == "evk_test"

    def test_headers_without_key(self):
        headers = self.client._headers()
        assert "X-API-Key" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_key(self):
        c = GatewayClient(BASE_URL, api_key="evk_test")
        headers = c._headers()
        assert headers["X-API-Key"] == "evk_test"

# =========================================================================
# Agent Client Tests
# =========================================================================

class TestAgentClient:
    def setup_method(self):
        self.client = AgentClient(AGENT_URL, api_key=None)

    def test_init(self):
        assert self.client.url == AGENT_URL

    def test_headers(self):
        headers = self.client._headers()
        assert "Content-Type" in headers

# =========================================================================
# Memory Client Tests
# =========================================================================

class TestMemoryClient:
    def setup_method(self):
        self.client = MemoryClient(AGENT_URL, api_key=None)

    def test_init(self):
        assert self.client.url == AGENT_URL

    def test_headers(self):
        headers = self.client._headers()
        assert "Content-Type" in headers

# =========================================================================
# Blockchain Client Tests
# =========================================================================

class TestBlockchainClient:
    def setup_method(self):
        self.client = BlockchainClient(BLOCKCHAIN_URL, api_key=None)

    def test_init(self):
        assert self.client.url == BLOCKCHAIN_URL

    def test_headers(self):
        headers = self.client._headers()
        assert "Content-Type" in headers

# =========================================================================
# Main Client Tests
# =========================================================================

class TestEvolvixOSClient:
    def test_init_default(self):
        client = EvolvixOSClient()
        assert client.base_url == "https://evolvixos.com"
        assert client.api_key is None
        assert client.gateway is not None
        assert client.agents is not None
        assert client.memory is not None
        assert client.blockchain is not None

    def test_init_custom(self):
        client = EvolvixOSClient(
            base_url="https://custom.example.com",
            api_key="evk_custom",
        )
        assert client.base_url == "https://custom.example.com"
        assert client.api_key == "evk_custom"

    def test_init_trailing_slash(self):
        client = EvolvixOSClient(base_url="https://evolvixos.com/")
        assert client.base_url == "https://evolvixos.com"

    def test_subclients_share_api_key(self):
        client = EvolvixOSClient(api_key="evk_shared")
        assert client.gateway.api_key == "evk_shared"
        assert client.agents.api_key == "evk_shared"
        assert client.memory.api_key == "evk_shared"
        assert client.blockchain.api_key == "evk_shared"

    def test_custom_urls(self):
        client = EvolvixOSClient(
            gateway_url="http://gateway:3500",
            agent_url="http://agents:3600",
            blockchain_url="http://blockchain:3200",
        )
        assert client.gateway.url == "http://gateway:3500"
        assert client.agents.url == "http://agents:3600"
        assert client.memory.url == "http://agents:3600"
        assert client.blockchain.url == "http://blockchain:3200"

# =========================================================================
# Integration Tests (require running services)
# =========================================================================

class TestIntegration:
    """Integration tests that require running services"""
    
    @pytest.fixture
    def client(self):
        return EvolvixOSClient(
            gateway_url="http://localhost:3500",
            agent_url="http://localhost:3600",
            blockchain_url="http://localhost:3200",
        )

    @pytest.mark.asyncio
    async def test_gateway_health(self, client):
        result = await client.gateway.health()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_gateway_list_plugins(self, client):
        result = await client.gateway.list_plugins()
        assert "plugins" in result

    @pytest.mark.asyncio
    async def test_agent_health(self, client):
        result = await client.agents.framework_stats()
        assert "total_agents" in result

    @pytest.mark.asyncio
    async def test_full_workflow(self, client):
        """Full workflow: create agent → start → store memory → create task → execute"""
        # Create agent
        agent = await client.agents.create(
            name="SDK Test Agent",
            capabilities=["chat", "sentiment"],
            system_prompt="You are a test agent.",
        )
        assert agent["name"] == "SDK Test Agent"
        agent_id = agent["id"]

        # Start agent
        await client.agents.start(agent_id)

        # Store memory
        mem = await client.memory.store(agent_id, "test_key", "test_value")
        assert mem["key"] == "test_key"

        # Retrieve memory
        retrieved = await client.memory.get(agent_id, "test_key")
        assert retrieved["value"] == "test_value"

        # Create and execute sentiment task
        task = await client.agents.create_task(agent_id, "sentiment", {"text": "I love EvolvixOS!"})
        assert task["status"] == "pending"

        result = await client.agents.execute_task(agent_id, task["id"])
        assert result["status"] in ("completed", "failed")

        # Check agent stats
        stats = await client.agents.stats(agent_id)
        assert stats["name"] == "SDK Test Agent"

        # Cleanup
        await client.agents.delete(agent_id)
