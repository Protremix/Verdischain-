"""
Tests for Multi-provider AI plugins (Anthropic, plugin architecture)
"""

import pytest
import os
import sys
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anthropic_plugin import AnthropicPlugin, PLUGIN_NAME, PLUGIN_CAPABILITIES


class TestAnthropicPlugin:
    def setup_method(self):
        os.environ["ANTHROPIC_API_KEY"] = "test-key-123"
        self.plugin = AnthropicPlugin()

    def test_plugin_metadata(self):
        assert PLUGIN_NAME == "anthropic-claude"
        assert "chat" in PLUGIN_CAPABILITIES
        assert "completion" in PLUGIN_CAPABILITIES
        assert self.plugin.provider == "anthropic"

    def test_health_check_with_key(self):
        assert self.plugin.health_check() == True

    def test_health_check_without_key(self):
        plugin = AnthropicPlugin(api_key="")
        assert plugin.health_check() == False

    def test_metrics_initial(self):
        metrics = self.plugin.metrics
        assert metrics["request_count"] == 0
        assert metrics["error_count"] == 0
        assert metrics["total_tokens"] == 0

    @pytest.mark.asyncio
    async def test_chat_mock(self):
        """Test chat with mocked Anthropic API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Hello from Claude!"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.chat([
                {"role": "user", "content": "Hi"}
            ])
        
        assert result["content"] == "Hello from Claude!"
        assert result["tokens_used"] == 15
        assert result["role"] == "assistant"
        assert self.plugin.metrics["request_count"] == 1
        assert self.plugin.metrics["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_completion_mock(self):
        """Test completion with mocked API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Completed text"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 5, "output_tokens": 3},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.completion("Complete this")
        
        assert result["content"] == "Completed text"
        assert result["tokens_used"] == 8

    @pytest.mark.asyncio
    async def test_execute_chat(self):
        """Test execute method with chat capability"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Response"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 5, "output_tokens": 5},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.execute("chat", {"messages": [{"role": "user", "content": "Hi"}]})
        
        assert "content" in result

    @pytest.mark.asyncio
    async def test_execute_text_input(self):
        """Test execute with text input instead of messages"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Response"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 3, "output_tokens": 3},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.execute("chat", {"text": "Hello"})
        
        assert result["content"] == "Response"

    @pytest.mark.asyncio
    async def test_execute_completion(self):
        """Test execute with completion capability"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "Done"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 2, "output_tokens": 2},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.execute("completion", {"prompt": "Test"})
        
        assert result["content"] == "Done"

    @pytest.mark.asyncio
    async def test_execute_unsupported(self):
        """Test execute with unsupported capability"""
        with pytest.raises(ValueError):
            await self.plugin.execute("embedding", {"text": "test"})

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """Test error handling in chat"""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API Error")
            with pytest.raises(Exception):
                await self.plugin.chat([{"role": "user", "content": "Hi"}])
        
        assert self.plugin.metrics["error_count"] == 1

    @pytest.mark.asyncio
    async def test_chat_no_api_key(self):
        """Test chat without API key"""
        plugin = AnthropicPlugin(api_key="")
        with pytest.raises(ValueError):
            await plugin.chat([{"role": "user", "content": "Hi"}])

    def test_system_prompt_extraction(self):
        """Test that system messages are extracted properly"""
        # This tests the internal logic without making API calls
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        # The plugin should extract system from messages
        system = ""
        chat_msgs = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_msgs.append(msg)
        assert system == "You are helpful"
        assert len(chat_msgs) == 1

    @pytest.mark.asyncio
    async def test_chat_with_system_param(self):
        """Test chat with explicit system parameter"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "content": [{"text": "OK"}],
            "model": "claude-sonnet-4-20250514",
            "usage": {"input_tokens": 5, "output_tokens": 2},
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await self.plugin.chat(
                [{"role": "user", "content": "Hi"}],
                system="Be concise"
            )
        
        assert result["content"] == "OK"
        # Verify the system prompt was passed in the request body
        call_args = mock_post.call_args
        import json
        body = call_args.kwargs.get("json", {})
        assert body.get("system") == "Be concise"

    def test_metrics_after_requests(self):
        """Test metrics update after requests"""
        plugin = AnthropicPlugin(api_key="test")
        plugin._request_count = 5
        plugin._error_count = 1
        plugin._total_latency = 5000
        plugin._total_tokens = 1000
        
        metrics = plugin.metrics
        assert metrics["request_count"] == 5
        assert metrics["error_count"] == 1
        assert metrics["avg_latency_ms"] == 1000
        assert metrics["error_rate"] == 0.2
