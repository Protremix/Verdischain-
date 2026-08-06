"""Tests for EvolvixOS Developer CLI v1.0"""

import pytest
import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from argparse import Namespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evolvixos_cli import EvolvixOSClient, cmd_init, cmd_status, cmd_contracts, cmd_agents, cmd_plugins, cmd_login, cmd_docs, main


class TestEvolvixOSClient:
    def test_client_initialization(self):
        client = EvolvixOSClient()
        assert client.api_url == "https://evolvixos.com"
        assert client.api_key == ""
    
    def test_client_with_custom_url(self):
        client = EvolvixOSClient(api_url="https://custom.example.com", api_key="test-key")
        assert client.api_url == "https://custom.example.com"
        assert client.api_key == "test-key"
    
    def test_client_headers(self):
        client = EvolvixOSClient(api_key="test-key")
        headers = client._headers()
        assert headers["X-API-Key"] == "test-key"
        assert headers["Content-Type"] == "application/json"
    
    def test_client_headers_no_key(self):
        client = EvolvixOSClient()
        headers = client._headers()
        assert "X-API-Key" not in headers
    
    def test_login_saves_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr("evolvixos_cli.CONFIG_DIR", tmp_path / ".evolvixos")
        monkeypatch.setattr("evolvixos_cli.CONFIG_FILE", tmp_path / ".evolvixos" / "config.json")
        
        client = EvolvixOSClient()
        result = client.login("test-api-key", "https://test.example.com")
        assert result["status"] == "ok"
        assert result["api_url"] == "https://test.example.com"
        assert (tmp_path / ".evolvixos" / "config.json").exists()
    
    def test_load_config(self, tmp_path, monkeypatch):
        config_dir = tmp_path / ".evolvixos"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text(json.dumps({"api_url": "https://loaded.example.com", "api_key": "loaded-key"}))
        
        monkeypatch.setattr("evolvixos_cli.CONFIG_DIR", config_dir)
        monkeypatch.setattr("evolvixos_cli.CONFIG_FILE", config_file)
        
        client = EvolvixOSClient()
        assert client.api_url == "https://loaded.example.com"
        assert client.api_key == "loaded-key"


class TestCLICommands:
    def test_cmd_init_creates_project(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        client = EvolvixOSClient()
        args = Namespace(project_name="test-project", template=None)
        result = cmd_init(client, args)
        assert result == 0
        assert (tmp_path / "test-project").exists()
        assert (tmp_path / "test-project" / "contracts").exists()
        assert (tmp_path / "test-project" / "tests").exists()
        assert (tmp_path / "test-project" / "scripts").exists()
        assert (tmp_path / "test-project" / "evolvixos.json").exists()
        assert (tmp_path / "test-project" / "contracts" / "Example.sol").exists()
        assert (tmp_path / "test-project" / "README.md").exists()
        assert (tmp_path / "test-project" / ".gitignore").exists()
    
    def test_cmd_init_existing_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "existing").mkdir()
        client = EvolvixOSClient()
        args = Namespace(project_name="existing", template=None)
        result = cmd_init(client, args)
        assert result == 1
    
    def test_cmd_init_config_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        client = EvolvixOSClient()
        args = Namespace(project_name="my-project", template=None)
        cmd_init(client, args)
        config = json.loads((tmp_path / "my-project" / "evolvixos.json").read_text())
        assert config["name"] == "my-project"
        assert config["version"] == "1.0.0"
        assert config["network"] == "verdis-testnet"
    
    def test_cmd_docs(self, capsys):
        client = EvolvixOSClient()
        result = cmd_docs(client, Namespace())
        assert result == 0
        captured = capsys.readouterr()
        assert "EvolvixOS API Documentation" in captured.out
        assert "/contracts/" in captured.out
    
    def test_cmd_login(self, tmp_path, monkeypatch):
        monkeypatch.setattr("evolvixos_cli.CONFIG_DIR", tmp_path / ".evolvixos")
        monkeypatch.setattr("evolvixos_cli.CONFIG_FILE", tmp_path / ".evolvixos" / "config.json")
        
        client = EvolvixOSClient()
        args = Namespace(api_key="test-key", api_url="https://test.example.com")
        result = cmd_login(client, args)
        assert result == 0
    
    def test_main_no_command(self, capsys):
        with patch("sys.argv", ["evolvixos"]):
            result = main()
            assert result == 1
            captured = capsys.readouterr()
            assert "evolvixos" in captured.out


class TestCLIContractsCommands:
    def test_cmd_contracts_templates(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={
            "templates": [
                {"name": "ERC20 Token", "category": "tokens", "tags": ["token", "erc20"]},
                {"name": "Carbon Credit", "category": "eco", "tags": ["eco", "carbon"]},
            ]
        }):
            args = Namespace(contracts_command="templates")
            result = cmd_contracts(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "ERC20 Token" in captured.out
            assert "Carbon Credit" in captured.out
    
    def test_cmd_contracts_list_empty(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={"contracts": [], "count": 0}):
            args = Namespace(contracts_command="list")
            result = cmd_contracts(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "No contracts" in captured.out
    
    def test_cmd_contracts_list_with_data(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={
            "contracts": [
                {"id": "abc123de", "name": "TestToken", "status": "deployed", "language": "solidity"},
            ],
            "count": 1
        }):
            args = Namespace(contracts_command="list")
            result = cmd_contracts(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "TestToken" in captured.out
    
    def test_cmd_contracts_generate(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={
            "generated": True,
            "name": "CustomToken_20260806",
            "source_code": "contract CustomToken { }",
            "language": "solidity",
        }):
            args = Namespace(contracts_command="generate", description="My token", type="token")
            result = cmd_contracts(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "CustomToken" in captured.out
    
    def test_cmd_contracts_create_no_source(self, capsys):
        client = EvolvixOSClient()
        args = Namespace(contracts_command="create", name="Test", source=None)
        result = cmd_contracts(client, args)
        assert result == 1


class TestCLIAgentsCommands:
    def test_cmd_agents_list_empty(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={"agents": []}):
            args = Namespace(agents_command="list")
            result = cmd_agents(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "No agents" in captured.out
    
    def test_cmd_agents_list_with_data(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={
            "agents": [
                {"name": "CodeReviewer", "role": "developer", "status": "running"},
            ]
        }):
            args = Namespace(agents_command="list")
            result = cmd_agents(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "CodeReviewer" in captured.out


class TestCLIPluginsCommands:
    def test_cmd_plugins_list_empty(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={"plugins": []}):
            args = Namespace(plugins_command="list")
            result = cmd_plugins(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "No plugins" in captured.out
    
    def test_cmd_plugins_list_with_data(self, capsys):
        client = EvolvixOSClient()
        with patch.object(client, '_request', new_callable=AsyncMock, return_value={
            "plugins": [
                {"name": "openai-gpt4o", "type": "llm_provider", "active": True},
            ]
        }):
            args = Namespace(plugins_command="list")
            result = cmd_plugins(client, args)
            assert result == 0
            captured = capsys.readouterr()
            assert "openai-gpt4o" in captured.out
