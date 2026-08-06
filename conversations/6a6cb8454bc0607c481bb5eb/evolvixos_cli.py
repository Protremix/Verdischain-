#!/usr/bin/env python3
"""
EvolvixOS Developer CLI v1.0
Command-line interface for EvolvixOS platform interaction

Usage:
    evolvixos init [project_name] [--template <name>]
    evolvixos deploy [contract_id] [--network <network>]
    evolvixos agents list
    evolvixos agents create <name> [--role <role>]
    evolvixos contracts list
    evolvixos contracts create <name> --source <file>
    evolvixos contracts templates
    evolvixos contracts generate --description <text> --type <type>
    evolvixos plugins list
    evolvixos plugins install <name>
    evolvixos status
    evolvixos login --api-key <key>
    evolvixos docs
"""

import argparse
import os
import sys
import json
import httpx
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Configuration
DEFAULT_API_URL = "https://evolvixos.com"
CONFIG_DIR = Path.home() / ".evolvixos"
CONFIG_FILE = CONFIG_DIR / "config.json"


class EvolvixOSClient:
    """HTTP client for EvolvixOS API."""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv("EVOLVIXOS_API_URL", DEFAULT_API_URL)
        self.api_key = api_key or os.getenv("EVOLVIXOS_API_KEY", "")
        self._load_config()
    
    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                config = json.loads(CONFIG_FILE.read_text())
                if not self.api_url or self.api_url == DEFAULT_API_URL:
                    self.api_url = config.get("api_url", self.api_url)
                if not self.api_key:
                    self.api_key = config.get("api_key", "")
            except: pass
    
    def _save_config(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(json.dumps({
            "api_url": self.api_url,
            "api_key": self.api_key,
        }, indent=2))
    
    def _headers(self) -> Dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
    
    async def _request(self, method: str, path: str, **kwargs) -> Dict:
        url = f"{self.api_url}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method, url, headers=self._headers(), **kwargs)
            if resp.status_code >= 400:
                return {"error": resp.status_code, "detail": resp.text[:200]}
            try:
                return resp.json()
            except:
                return {"raw": resp.text[:500]}
    
    # Status
    async def status(self) -> Dict:
        return await self._request("GET", "/ai-gateway/health")
    
    # Contracts
    async def contracts_list(self) -> Dict:
        return await self._request("GET", "/contracts/api/v1/contracts/")
    
    async def contracts_templates(self) -> Dict:
        return await self._request("GET", "/contracts/api/v1/contracts/templates/all")
    
    async def contracts_create(self, name: str, source_file: str) -> Dict:
        source = Path(source_file).read_text()
        return await self._request("POST", "/contracts/api/v1/contracts/", json={
            "name": name, "source_code": source, "language": "solidity"
        })
    
    async def contracts_generate(self, description: str, contract_type: str = "token") -> Dict:
        return await self._request("POST", "/contracts/api/v1/contracts/ai/generate", json={
            "description": description, "contract_type": contract_type
        })
    
    async def contracts_deploy(self, contract_id: str, network: str = "verdis-testnet") -> Dict:
        return await self._request("POST", f"/contracts/api/v1/contracts/{contract_id}/deploy", json={
            "network": network
        })
    
    async def contracts_test(self, contract_id: str, test_name: str = "test_all") -> Dict:
        return await self._request("POST", f"/contracts/api/v1/contracts/{contract_id}/test", json={
            "contract_id": contract_id, "test_name": test_name
        })
    
    # Agents
    async def agents_list(self) -> Dict:
        return await self._request("GET", "/agents/agents")
    
    async def agent_create(self, name: str, role: str = "developer") -> Dict:
        return await self._request("POST", "/agents/agents", json={"name": name, "role": role})
    
    # Gateway
    async def gateway_plugins(self) -> Dict:
        return await self._request("GET", "/ai-gateway/plugins")
    
    async def gateway_invoke(self, capability: str, input_data: Dict) -> Dict:
        return await self._request("POST", "/ai-gateway/invoke", json={
            "capability": capability, "input_data": input_data
        })
    
    # Queue
    async def queue_stats(self) -> Dict:
        return await self._request("GET", "/queue/agent/stats")
    
    # Monitoring
    async def monitoring_health(self) -> Dict:
        return await self._request("GET", "/monitoring/health")
    
    # Enterprise
    async def enterprise_dashboard(self) -> Dict:
        return await self._request("GET", "/enterprise/api/v1/enterprise/dashboard")
    
    # RBAC
    async def rbac_dashboard(self) -> Dict:
        return await self._request("GET", "/rbac/api/v1/rbac/dashboard")
    
    # Auth
    def login(self, api_key: str, api_url: str = None):
        self.api_key = api_key
        if api_url:
            self.api_url = api_url
        self._save_config()
        return {"status": "ok", "api_url": self.api_url}


# =========================================================================
# CLI Commands
# =========================================================================

def cmd_init(client: EvolvixOSClient, args):
    """Initialize a new EvolvixOS project."""
    project_name = args.project_name or "evolvixos-project"
    project_dir = Path(project_name)
    
    if project_dir.exists():
        print(f"Error: Directory '{project_name}' already exists")
        return 1
    
    project_dir.mkdir(parents=True)
    
    # Create project structure
    (project_dir / "contracts").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "scripts").mkdir()
    
    # Create config file
    config = {
        "name": project_name,
        "version": "1.0.0",
        "network": "verdis-testnet",
        "compiler_version": "0.8.24",
        "api_url": client.api_url,
    }
    (project_dir / "evolvixos.json").write_text(json.dumps(config, indent=2))
    
    # Create example contract
    if args.template:
        templates = asyncio.run(client.contracts_templates())
        template = None
        for t in templates.get("templates", []):
            if t["name"].lower().replace(" ", "-") == args.template.lower():
                template = t
                break
        if template:
            (project_dir / "contracts" / "Example.sol").write_text(template["source_code"])
            print(f"Initialized '{project_name}' with template: {template['name']}")
        else:
            print(f"Template '{args.template}' not found. Using default.")
            _write_default_contract(project_dir)
    else:
        _write_default_contract(project_dir)
        print(f"Initialized '{project_name}' with default ERC20 template")
    
    # Create README
    (project_dir / "README.md").write_text(f"""# {project_name}

EvolvixOS smart contract project.

## Commands
- `evolvixos contracts list` — List contracts
- `evolvixos contracts templates` — List templates
- `evolvixos contracts generate --description "My token" --type token` — AI generate
- `evolvixos deploy <contract_id>` — Deploy contract
- `evolvixos status` — Check platform status

## Structure
- `contracts/` — Solidity source files
- `tests/` — Contract tests
- `scripts/` — Deployment scripts
""")
    
    # Create .gitignore
    (project_dir / ".gitignore").write_text("node_modules/\n*.pyc\n__pycache__/\n.env\nbuild/\n")
    
    print(f"Project structure created in ./{project_name}/")
    return 0


def _write_default_contract(project_dir: Path):
    (project_dir / "contracts" / "Example.sol").write_text("""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ExampleToken {
    string public name = "Example Token";
    string public symbol = "EXT";
    uint8 public decimals = 18;
    uint256 public totalSupply = 1000000000 * 10**18;
    
    mapping(address => uint256) public balanceOf;
    
    constructor() {
        balanceOf[msg.sender] = totalSupply;
    }
    
    function transfer(address to, uint256 amount) public returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}""")


def cmd_status(client: EvolvixOSClient, args):
    """Check EvolvixOS platform status."""
    print("EvolvixOS Platform Status")
    print("=" * 40)
    
    services = [
        ("AI Gateway", "/ai-gateway/health"),
        ("Contracts", "/contracts/health"),
        ("Monitoring", "/monitoring/health"),
        ("Queue", "/queue/agent/stats"),
        ("RBAC", "/rbac/dashboard"),
        ("Enterprise", "/enterprise/dashboard"),
    ]
    
    for name, path in services:
        try:
            result = asyncio.run(client._request("GET", path))
            if "error" in result:
                print(f"  {name:20s} ✗ (HTTP {result['error']})")
            else:
                status = result.get("status", "ok")
                print(f"  {name:20s} ✓")
        except Exception as e:
            print(f"  {name:20s} ✗ ({str(e)[:30]})")
    
    return 0


def cmd_contracts(client: EvolvixOSClient, args):
    """Contract management commands."""
    if args.contracts_command == "list":
        result = asyncio.run(client.contracts_list())
        contracts = result.get("contracts", [])
        if not contracts:
            print("No contracts found.")
            return 0
        print(f"Contracts ({result.get('count', len(contracts))}):")
        for c in contracts[:20]:
            print(f"  {c.get('id','?')[:8]}  {c.get('name','?'):30s}  {c.get('status','?'):10s}  {c.get('language','?')}")
    
    elif args.contracts_command == "templates":
        result = asyncio.run(client.contracts_templates())
        templates = result.get("templates", [])
        print(f"Contract Templates ({len(templates)}):")
        for t in templates:
            print(f"  {t['name']:25s}  {t['category']:15s}  tags: {', '.join(t.get('tags', []))}")
    
    elif args.contracts_command == "create":
        if not args.source:
            print("Error: --source required")
            return 1
        result = asyncio.run(client.contracts_create(args.name, args.source))
        if "error" in result:
            print(f"Error: {result.get('detail', 'Failed')}")
            return 1
        print(f"Contract created: {result.get('id', '?')}")
    
    elif args.contracts_command == "generate":
        result = asyncio.run(client.contracts_generate(args.description, args.type))
        if "error" in result:
            print(f"Error: {result.get('detail', 'Failed')}")
            return 1
        print(f"Generated: {result.get('name', '?')}")
        print(f"Language: {result.get('language', 'solidity')}")
        print(f"\nSource code:")
        print("-" * 40)
        print(result.get("source_code", "")[:500])
    
    elif args.contracts_command == "deploy":
        result = asyncio.run(client.contracts_deploy(args.contract_id, args.network))
        if "error" in result:
            print(f"Error: {result.get('detail', 'Failed')}")
            return 1
        print(f"Deployed: {result.get('address', '?')}")
        print(f"TX Hash: {result.get('tx_hash', '?')}")
        print(f"Network: {args.network}")
    
    elif args.contracts_command == "test":
        result = asyncio.run(client.contracts_test(args.contract_id, args.test_name or "test_all"))
        if "error" in result:
            print(f"Error: {result.get('detail', 'Failed')}")
            return 1
        print(f"Test: {result.get('status', '?')}")
        test_result = result.get("result", {})
        if test_result:
            print(f"  Passed: {test_result.get('tests_passed', '?')}/{test_result.get('tests_run', '?')}")
            print(f"  Coverage: {test_result.get('coverage', '?')}%")
            print(f"  Gas: {test_result.get('gas_estimate', '?')}")
    
    return 0


def cmd_agents(client: EvolvixOSClient, args):
    """Agent management commands."""
    if args.agents_command == "list":
        result = asyncio.run(client.agents_list())
        agents = result if isinstance(result, list) else result.get("agents", [])
        if not agents:
            print("No agents found.")
            return 0
        print(f"Agents ({len(agents)}):")
        for a in agents[:20]:
            name = a.get("name", "?")
            role = a.get("role", "?")
            status = a.get("status", "?")
            print(f"  {name:25s}  {role:15s}  {status}")
    elif args.agents_command == "create":
        result = asyncio.run(client.agent_create(args.name, args.role))
        if "error" in result:
            print(f"Error: {result.get('detail', 'Failed')}")
            return 1
        print(f"Agent created: {result.get('id', result.get('name', '?'))}")
    return 0


def cmd_plugins(client: EvolvixOSClient, args):
    """Plugin management commands."""
    if args.plugins_command == "list":
        result = asyncio.run(client.gateway_plugins())
        plugins = result if isinstance(result, list) else result.get("plugins", [])
        if not plugins:
            print("No plugins found.")
            return 0
        print(f"Gateway Plugins ({len(plugins)}):")
        for p in plugins[:20]:
            name = p.get("name", "?") if isinstance(p, dict) else str(p)
            ptype = p.get("type", "?") if isinstance(p, dict) else "?"
            active = "✓" if (isinstance(p, dict) and p.get("active", True)) else "✗"
            print(f"  {active} {name:30s}  {ptype}")
    elif args.plugins_command == "install":
        print(f"Plugin installation for '{args.plugin_name}' — coming in Phase 120")
    return 0


def cmd_login(client: EvolvixOSClient, args):
    """Login with API key."""
    result = client.login(args.api_key, args.api_url)
    print(f"Logged in to {result['api_url']}")
    print(f"Config saved to {CONFIG_FILE}")
    return 0


def cmd_docs(client: EvolvixOSClient, args):
    """Show API documentation."""
    print("EvolvixOS API Documentation")
    print("=" * 40)
    print("\nEndpoints:")
    endpoints = [
        ("Contracts", "/contracts/api/v1/contracts/"),
        ("Templates", "/contracts/api/v1/contracts/templates/all"),
        ("AI Generate", "/contracts/api/v1/contracts/ai/generate"),
        ("Agents", "/agents/agents"),
        ("Gateway", "/ai-gateway/invoke"),
        ("Queue", "/queue/agent/stats"),
        ("Monitoring", "/monitoring/health"),
        ("RBAC", "/rbac/api/v1/rbac/dashboard"),
        ("Enterprise", "/enterprise/api/v1/enterprise/dashboard"),
    ]
    for name, path in endpoints:
        print(f"  {name:20s}  {client.api_url}{path}")
    print(f"\nFull docs: {client.api_url}/monitoring/api-reference")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="evolvixos",
        description="EvolvixOS Developer CLI v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--api-url", default=None, help="API URL override")
    parser.add_argument("--api-key", default=None, help="API key override")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("project_name", nargs="?", default="evolvixos-project")
    init_parser.add_argument("--template", default=None, help="Contract template name")
    
    # status
    subparsers.add_parser("status", help="Check platform status")
    
    # contracts
    contracts_parser = subparsers.add_parser("contracts", help="Contract management")
    contracts_sub = contracts_parser.add_subparsers(dest="contracts_command")
    contracts_sub.add_parser("list", help="List contracts")
    contracts_sub.add_parser("templates", help="List templates")
    create_parser = contracts_sub.add_parser("create", help="Create contract")
    create_parser.add_argument("name", help="Contract name")
    create_parser.add_argument("--source", required=True, help="Source file path")
    gen_parser = contracts_sub.add_parser("generate", help="AI generate contract")
    gen_parser.add_argument("--description", required=True, help="Contract description")
    gen_parser.add_argument("--type", default="token", help="Contract type")
    deploy_parser = contracts_sub.add_parser("deploy", help="Deploy contract")
    deploy_parser.add_argument("contract_id", help="Contract ID")
    deploy_parser.add_argument("--network", default="verdis-testnet", help="Network")
    test_parser = contracts_sub.add_parser("test", help="Test contract")
    test_parser.add_argument("contract_id", help="Contract ID")
    test_parser.add_argument("--test-name", default="test_all", help="Test name")
    
    # agents
    agents_parser = subparsers.add_parser("agents", help="Agent management")
    agents_sub = agents_parser.add_subparsers(dest="agents_command")
    agents_sub.add_parser("list", help="List agents")
    create_agent = agents_sub.add_parser("create", help="Create agent")
    create_agent.add_argument("name", help="Agent name")
    create_agent.add_argument("--role", default="developer", help="Agent role")
    
    # plugins
    plugins_parser = subparsers.add_parser("plugins", help="Plugin management")
    plugins_sub = plugins_parser.add_subparsers(dest="plugins_command")
    plugins_sub.add_parser("list", help="List plugins")
    install_parser = plugins_sub.add_parser("install", help="Install plugin")
    install_parser.add_argument("plugin_name", help="Plugin name")
    
    # login
    login_parser = subparsers.add_parser("login", help="Login with API key")
    login_parser.add_argument("--api-key", required=True, help="API key")
    login_parser.add_argument("--api-url", default=None, help="API URL")
    
    # docs
    subparsers.add_parser("docs", help="Show API documentation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    client = EvolvixOSClient(api_url=args.api_url, api_key=args.api_key)
    
    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "contracts": cmd_contracts,
        "agents": cmd_agents,
        "plugins": cmd_plugins,
        "login": cmd_login,
        "docs": cmd_docs,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(client, args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
