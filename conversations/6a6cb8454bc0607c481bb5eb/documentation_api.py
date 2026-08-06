"""
EvolvixOS Documentation System — Auto-generated API docs, developer guides, and architecture references
Provides structured documentation accessible via API
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="EvolvixOS Documentation",
    description="Auto-generated documentation and developer guides",
    version="1.0.0",
)

# =========================================================================
# Documentation Data
# =========================================================================

ARCHITECTURE_OVERVIEW = {
    "title": "EvolvixOS Architecture",
    "version": "2.0.0",
    "description": "EvolvixOS is an AI-native engineering operating system built on a Substrate blockchain (Verdis). It combines autonomous AI agents, a unified AI gateway with intelligent routing, persistent long-term memory, and production-grade blockchain infrastructure.",
    "components": [
        {"name": "Blockchain Core", "tech": "Rust + Substrate", "description": "BABE/GRANDPA consensus, 7 FRAME pallets, EVM support", "tests": 232},
        {"name": "AI Gateway", "tech": "Python + FastAPI", "description": "Plugin architecture, intelligent routing, caching, rate limiting, security", "tests": 80},
        {"name": "Agent Framework", "tech": "Python + FastAPI", "description": "Autonomous agents, task execution, 5 memory types, PostgreSQL persistence", "tests": 73},
        {"name": "Developer SDK", "tech": "Python + TypeScript", "description": "Unified SDK for gateway, agents, memory, and blockchain", "tests": 34},
        {"name": "Production Infrastructure", "tech": "Docker + Nginx", "description": "16 containers, monitoring, log aggregation, automated backups", "tests": 0},
    ],
    "total_tests": 419,
    "containers": 16,
    "domains": ["evolvixos.com", "verdischain.com"],
}

API_REFERENCE = {
    "ai_gateway": {
        "base_url": "https://evolvixos.com/ai-gateway",
        "endpoints": [
            {"method": "POST", "path": "/gateway/invoke", "description": "Invoke an AI capability", "auth": "optional"},
            {"method": "GET", "path": "/health", "description": "Gateway health check", "auth": "none"},
            {"method": "GET", "path": "/plugins", "description": "List registered plugins", "auth": "none"},
            {"method": "POST", "path": "/plugins/register", "description": "Register a new plugin", "auth": "api-key"},
            {"method": "DELETE", "path": "/plugins/{name}", "description": "Unregister a plugin", "auth": "api-key"},
            {"method": "GET", "path": "/gateway/stats", "description": "Gateway statistics", "auth": "api-key"},
            {"method": "GET", "path": "/capabilities", "description": "List available capabilities", "auth": "api-key"},
            {"method": "POST", "path": "/cache/clear", "description": "Clear response cache", "auth": "api-key"},
            {"method": "POST", "path": "/api-keys/create", "description": "Create API key", "auth": "api-key"},
            {"method": "GET", "path": "/api-keys", "description": "List API keys", "auth": "api-key"},
            {"method": "GET", "path": "/api-keys/{key_id}", "description": "Get API key details", "auth": "api-key"},
            {"method": "DELETE", "path": "/api-keys/{key_id}", "description": "Revoke API key", "auth": "api-key"},
            {"method": "GET", "path": "/api-keys/{key_id}/usage", "description": "Get API key usage stats", "auth": "api-key"},
        ],
        "plugins": ["openai-gpt4o", "sentiment-analyzer", "code-reviewer", "anthropic-claude"],
    },
    "agent_framework": {
        "base_url": "https://evolvixos.com/agents",
        "endpoints": [
            {"method": "POST", "path": "/agents", "description": "Create a new agent", "auth": "none"},
            {"method": "GET", "path": "/agents", "description": "List agents", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}", "description": "Get agent by ID", "auth": "none"},
            {"method": "PATCH", "path": "/agents/{id}", "description": "Update agent", "auth": "none"},
            {"method": "DELETE", "path": "/agents/{id}", "description": "Delete agent", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/start", "description": "Start agent", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/pause", "description": "Pause agent", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/stop", "description": "Stop agent", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}/stats", "description": "Agent statistics", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/tasks", "description": "Create task for agent", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/tasks/{task_id}/execute", "description": "Execute task via Gateway", "auth": "none"},
            {"method": "GET", "path": "/tasks", "description": "List tasks", "auth": "none"},
            {"method": "GET", "path": "/tasks/{id}", "description": "Get task by ID", "auth": "none"},
            {"method": "POST", "path": "/tasks/{id}/cancel", "description": "Cancel task", "auth": "none"},
            {"method": "POST", "path": "/agents/{id}/memory", "description": "Store memory entry", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}/memory/stats", "description": "Memory statistics", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}/memory", "description": "List memories", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}/memory/{key}", "description": "Get memory by key", "auth": "none"},
            {"method": "PATCH", "path": "/agents/{id}/memory/{key}", "description": "Update memory", "auth": "none"},
            {"method": "DELETE", "path": "/agents/{id}/memory/{key}", "description": "Delete memory", "auth": "none"},
            {"method": "GET", "path": "/agents/{id}/memory/search/{query}", "description": "Search memories", "auth": "none"},
            {"method": "DELETE", "path": "/agents/{id}/memory", "description": "Clear all memories", "auth": "none"},
            {"method": "POST", "path": "/memory/cleanup", "description": "Clean up expired memories", "auth": "none"},
            {"method": "GET", "path": "/health", "description": "Framework health", "auth": "none"},
            {"method": "GET", "path": "/stats", "description": "Framework statistics", "auth": "none"},
        ],
    },
    "blockchain": {
        "base_url": "https://evolvixos.com/blockchain/api",
        "endpoints": [
            {"method": "GET", "path": "/health", "description": "Blockchain health", "auth": "none"},
            {"method": "GET", "path": "/chain-state", "description": "Chain state", "auth": "none"},
            {"method": "GET", "path": "/blocks/latest", "description": "Latest block", "auth": "none"},
            {"method": "GET", "path": "/blocks/{number}", "description": "Block by height", "auth": "none"},
            {"method": "GET", "path": "/validators", "description": "Validator list", "auth": "none"},
            {"method": "GET", "path": "/dex/pools", "description": "DEX pools", "auth": "none"},
            {"method": "GET", "path": "/dex/prices", "description": "DEX prices", "auth": "none"},
            {"method": "GET", "path": "/tokenomics", "description": "Tokenomics data", "auth": "none"},
            {"method": "GET", "path": "/eco/stats", "description": "Eco/carbon stats", "auth": "none"},
        ],
    },
}

DEVELOPER_GUIDES = [
    {
        "id": "quickstart",
        "title": "Quick Start Guide",
        "description": "Get started with EvolvixOS in 5 minutes",
        "steps": [
            "Install the EvolvixOS SDK: pip install evolvixos-sdk",
            "Initialize the client: client = EvolvixOSClient(base_url='https://evolvixos.com', api_key='your-key')",
            "Create an agent: agent = await client.agents.create(name='My Agent', capabilities=['chat'])",
            "Start the agent: await client.agents.start(agent['id'])",
            "Execute a task: result = await client.agents.execute_task(agent['id'], task['id'])",
        ],
    },
    {
        "id": "agent-creation",
        "title": "Creating and Managing AI Agents",
        "description": "Complete guide to agent lifecycle management",
        "sections": ["Agent capabilities", "System prompts", "Memory types", "Task execution", "Error handling"],
    },
    {
        "id": "gateway-usage",
        "title": "Using the AI Gateway",
        "description": "How to use the AI Gateway for direct AI operations",
        "sections": ["Available capabilities", "Plugin selection", "Caching", "Rate limiting", "API keys"],
    },
    {
        "id": "memory-management",
        "title": "Agent Memory Management",
        "description": "Persistent memory for autonomous agents",
        "sections": ["Memory types (short_term, long_term, episodic, semantic, procedural)", "Importance scoring", "TTL expiry", "Search", "Memory context injection"],
    },
    {
        "id": "blockchain-integration",
        "title": "Blockchain Integration",
        "description": "Interacting with the Verdis blockchain",
        "sections": ["Reading blocks", "Validator queries", "DEX operations", "Tokenomics", "Carbon credits"],
    },
    {
        "id": "plugin-development",
        "title": "Developing Custom Gateway Plugins",
        "description": "How to create and register custom AI plugins",
        "sections": ["Plugin interface", "Capabilities", "Metrics", "Health checks", "Registration"],
    },
    {
        "id": "sdk-reference",
        "title": "SDK Reference (Python & TypeScript)",
        "description": "Complete API reference for both SDKs",
        "sections": ["Python SDK", "TypeScript SDK", "Authentication", "Error handling", "Configuration"],
    },
]

FAQS = [
    {"question": "What is EvolvixOS?", "answer": "EvolvixOS is an AI Engineering Operating System that combines autonomous AI agents, a unified AI gateway, persistent memory, and blockchain infrastructure."},
    {"question": "How do I get an API key?", "answer": "API keys can be created via the AI Gateway's /api-keys/create endpoint or through the SDK's gateway client."},
    {"question": "What AI providers are supported?", "answer": "Currently: OpenAI (GPT-4o) and Anthropic (Claude). The plugin architecture allows easy addition of new providers."},
    {"question": "What memory types are available?", "answer": "Five types: short_term, long_term, episodic, semantic, procedural — each with different persistence and access patterns."},
    {"question": "Is the blockchain required?", "answer": "No. The AI Gateway and Agent Framework work independently. Blockchain integration is optional."},
    {"question": "How are agents executed?", "answer": "Agents execute tasks by calling the AI Gateway, which routes to the appropriate plugin based on capability, reliability, latency, cost, and load."},
    {"question": "What is the total test count?", "answer": "419 tests across all components (232 Rust + 187 Python)."},
    {"question": "How do I deploy EvolvixOS?", "answer": "EvolvixOS runs as 16 Docker containers with Nginx reverse proxy. See the deployment guide for details."},
]

RUNBOOKS = [
    {
        "id": "gateway-down",
        "title": "AI Gateway Down",
        "severity": "critical",
        "steps": ["Check container: docker ps | grep ai-gateway", "Check logs: docker logs ai-gateway --tail 50", "Restart: docker restart ai-gateway", "Verify: curl http://localhost:3500/health", "If plugins missing: re-register via /plugins/register"],
    },
    {
        "id": "agent-framework-down",
        "title": "Agent Framework Down",
        "severity": "critical",
        "steps": ["Check container: docker ps | grep agent-framework", "Check logs: docker logs agent-framework --tail 50", "Restart: docker restart agent-framework", "Verify: curl http://localhost:3600/health", "Check PostgreSQL connectivity"],
    },
    {
        "id": "blockchain-stalled",
        "title": "Blockchain Not Producing Blocks",
        "severity": "critical",
        "steps": ["Check container: docker ps | grep verdis-node", "Check logs: docker logs verdis-node --tail 50", "Check RPC: curl -X POST http://localhost:9944 -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"method\":\"chain_head\",\"params\":[],\"id\":1}'", "Restart if needed: docker restart verdis-node"],
    },
    {
        "id": "high-error-rate",
        "title": "High Error Rate in Gateway",
        "severity": "warning",
        "steps": ["Check gateway stats: curl http://localhost:3500/gateway/stats", "Identify failing plugin", "Check plugin metrics", "Verify API keys are valid", "Check rate limiting configuration"],
    },
]

# =========================================================================
# Endpoints
# =========================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/architecture")
async def get_architecture():
    """Get the EvolvixOS architecture overview"""
    return ARCHITECTURE_OVERVIEW

@app.get("/api-reference")
async def get_api_reference(service: Optional[str] = None):
    """Get API reference for all services or a specific one"""
    if service:
        if service in API_REFERENCE:
            return API_REFERENCE[service]
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    return API_REFERENCE

@app.get("/guides")
async def list_guides():
    """List all developer guides"""
    return {"guides": DEVELOPER_GUIDES, "count": len(DEVELOPER_GUIDES)}

@app.get("/guides/{guide_id}")
async def get_guide(guide_id: str):
    """Get a specific guide"""
    for guide in DEVELOPER_GUIDES:
        if guide["id"] == guide_id:
            return guide
    raise HTTPException(status_code=404, detail="Guide not found")

@app.get("/faq")
async def list_faqs():
    """List FAQs"""
    return {"faqs": FAQS, "count": len(FAQS)}

@app.get("/runbooks")
async def list_runbooks():
    """List operational runbooks"""
    return {"runbooks": RUNBOOKS, "count": len(RUNBOOKS)}

@app.get("/runbooks/{runbook_id}")
async def get_runbook(runbook_id: str):
    """Get a specific runbook"""
    for runbook in RUNBOOKS:
        if runbook["id"] == runbook_id:
            return runbook
    raise HTTPException(status_code=404, detail="Runbook not found")

@app.get("/sdk/quickstart")
async def sdk_quickstart(language: str = "python"):
    """Get SDK quickstart code"""
    if language == "python":
        return {
            "language": "python",
            "code": '''# Install: pip install httpx
import asyncio
from evolvixos_sdk import EvolvixOSClient

async def main():
    client = EvolvixOSClient(
        base_url="https://evolvixos.com",
        api_key="your-api-key",
    )
    
    # Create and start an agent
    agent = await client.agents.create(
        name="My Assistant",
        capabilities=["chat", "sentiment"],
        system_prompt="You are a helpful assistant.",
    )
    await client.agents.start(agent["id"])
    
    # Store memory
    await client.memory.store(agent["id"], "context", "EvolvixOS project")
    
    # Execute a task
    task = await client.agents.create_task(
        agent["id"], "sentiment", {"text": "EvolvixOS is great!"}
    )
    result = await client.agents.execute_task(agent["id"], task["id"])
    print(f"Result: {result['output_data']}")
    
    # Cleanup
    await client.agents.delete(agent["id"])

asyncio.run(main())
''',
        }
    elif language == "typescript":
        return {
            "language": "typescript",
            "code": '''// npm install evolvixos-sdk
import { EvolvixOSClient } from 'evolvixos-sdk';

async function main() {
    const client = new EvolvixOSClient({
        baseUrl: 'https://evolvixos.com',
        apiKey: 'your-api-key',
    });
    
    // Create and start an agent
    const agent = await client.agents.create({
        name: 'My Assistant',
        capabilities: ['chat', 'sentiment'],
        systemPrompt: 'You are a helpful assistant.',
    });
    await client.agents.start(agent.id);
    
    // Store memory
    await client.memory.store(agent.id, 'context', 'EvolvixOS project');
    
    // Execute a task
    const task = await client.agents.createTask(
        agent.id, 'sentiment', { text: 'EvolvixOS is great!' }
    );
    const result = await client.agents.executeTask(agent.id, task.id);
    console.log('Result:', result.output_data);
    
    // Cleanup
    await client.agents.delete(agent.id);
}

main();
''',
        }
    else:
        raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")

@app.get("/stats")
async def doc_stats():
    """Documentation statistics"""
    return {
        "architecture_components": len(ARCHITECTURE_OVERVIEW["components"]),
        "api_endpoints": sum(len(s["endpoints"]) for s in API_REFERENCE.values()),
        "guides": len(DEVELOPER_GUIDES),
        "faqs": len(FAQS),
        "runbooks": len(RUNBOOKS),
        "total_tests": ARCHITECTURE_OVERVIEW["total_tests"],
        "containers": ARCHITECTURE_OVERVIEW["containers"],
    }
