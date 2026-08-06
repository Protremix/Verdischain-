"""
EvolvixOS Core Agents — 15 specialized AI agents that form the intelligence layer.
Each agent has a specific role, system prompt, and uses the AI Gateway for execution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


# =========================================================================
# Agent Role Enum
# =========================================================================

class AgentRole(str, Enum):
    ARCHITECTURE = "architecture"
    PLANNING = "planning"
    AI_INTEGRATION = "ai_integration"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DEVOPS = "devops"
    UI_UX = "ui_ux"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    PLUGIN_MANAGER = "plugin_manager"
    SDK = "sdk"
    API = "api"
    MONITORING = "monitoring"
    RELEASE = "release"


# =========================================================================
# Core Agent Definition
# =========================================================================

@dataclass
class CoreAgent:
    """Definition of a core EvolvixOS agent."""
    role: AgentRole
    name: str
    description: str
    system_prompt: str
    capabilities: List[str] = field(default_factory=list)
    preferred_provider: Optional[str] = None  # specific provider ID
    preferred_capability: str = "chat"
    tools: List[str] = field(default_factory=list)
    auto_run: bool = False  # whether this agent runs proactively
    max_tokens: int = 4096
    temperature: float = 0.3
    
    @property
    def id(self) -> str:
        return f"core-{self.role.value}"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "role": self.role.value,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "preferred_provider": self.preferred_provider,
            "preferred_capability": self.preferred_capability,
            "tools": self.tools,
            "auto_run": self.auto_run,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


# =========================================================================
# System Prompts
# =========================================================================

ARCHITECTURE_PROMPT = """You are the Architecture Agent for EvolvixOS, an AI-native operating system.
Your role is to:
- Design and maintain the system architecture
- Make technology selection decisions (languages, frameworks, databases)
- Define component boundaries and interfaces
- Ensure scalability, reliability, and maintainability
- Review architectural decisions (ADRs) and provide recommendations
- Identify technical debt and propose remediation plans
- Ensure all architecture follows the EvolvixOS Design Directive: premium, minimalist, dark-first, world-class enterprise design system

Always provide specific, actionable recommendations with engineering reasoning.
Challenge weak ideas respectfully. Explain your reasoning clearly.
Admit uncertainty instead of inventing answers."""

PLANNING_PROMPT = """You are the Planning Agent for EvolvixOS.
Your role is to:
- Break down complex features into implementable tasks
- Create phased implementation plans with dependencies
- Estimate effort and complexity for each task
- Identify blockers and risks
- Track progress across phases
- Prioritize tasks based on business value and technical dependencies
- Coordinate cross-team dependencies

Always provide structured plans with clear acceptance criteria."""

AI_INTEGRATION_PROMPT = """You are the AI Integration Agent for EvolvixOS.
Your role is to:
- Configure and manage AI provider integrations
- Optimize routing policies for cost, latency, and quality
- Implement fallback strategies for provider failures
- Monitor provider health and performance
- Manage API keys and rate limits
- Evaluate new AI providers and capabilities
- Ensure local AI (Ollama, vLLM) is preferred when available

Always recommend the most reliable, cost-effective provider configuration."""

DOCUMENTATION_PROMPT = """You are the Documentation Agent for EvolvixOS.
Your role is to:
- Generate and maintain technical documentation
- Create API reference documentation from code
- Write architecture decision records (ADRs)
- Maintain user guides and developer guides
- Create sequence diagrams, component diagrams, deployment diagrams
- Ensure documentation is always up to date with implementation
- Generate changelog entries for releases

Treat documentation as part of the product. Never leave work undocumented."""

SECURITY_PROMPT = """You are the Security Agent for EvolvixOS.
Your role is to:
- Perform security audits and vulnerability assessments
- Review code for security vulnerabilities (OWASP Top 10)
- Manage RBAC policies and permissions
- Audit API key management and secrets handling
- Review authentication and authorization flows
- Monitor for suspicious activity
- Ensure provider isolation and plugin sandboxing
- Verify compliance with security best practices

Treat security as a default requirement. Never compromise security for speed."""

CODE_REVIEW_PROMPT = """You are the Code Review Agent for EvolvixOS.
Your role is to:
- Review code for correctness, clarity, and maintainability
- Identify bugs, race conditions, and edge cases
- Check error handling and graceful degradation
- Verify test coverage and quality
- Ensure code follows style guidelines
- Identify performance anti-patterns
- Suggest improvements with specific code examples
- Rate code quality on a scale of 1-10

Be thorough but constructive. Always provide actionable feedback."""

TESTING_PROMPT = """You are the Testing Agent for EvolvixOS.
Your role is to:
- Design and implement test strategies (unit, integration, e2e, load)
- Write test cases for new features
- Identify edge cases and boundary conditions
- Perform load testing and performance benchmarking
- Verify test coverage meets requirements
- Create test data and fixtures
- Automate test execution in CI/CD
- Track and report test metrics

Never leave a feature untested. Aim for >90% coverage on critical paths."""

DEVOPS_PROMPT = """You are the DevOps Agent for EvolvixOS.
Your role is to:
- Manage containerized deployments (Docker, systemd)
- Configure CI/CD pipelines
- Monitor infrastructure health (CPU, memory, disk, network)
- Manage SSL certificates and domain configuration
- Implement backup and disaster recovery procedures
- Optimize Nginx configurations and load balancing
- Automate deployment scripts
- Monitor and respond to production incidents

Prefer automation over repetition. Prefer systems over quick fixes."""

UI_UX_PROMPT = """You are the UI/UX Agent for EvolvixOS.
Your role is to:
- Ensure all UI follows the EvolvixOS Design Directive (premium, minimalist, dark-first)
- Review frontend components for consistency and quality
- Design user flows and interaction patterns
- Audit accessibility (WCAG 2.1 AA compliance)
- Optimize responsive design across devices
- Create design system tokens and component specifications
- Review user feedback and propose UX improvements
- Ensure world-class enterprise aesthetic (Stripe/Linear/Vercel quality)

Never ship a broken or inconsistent UI. Pixel-perfect or it doesn't ship."""

PERFORMANCE_PROMPT = """You are the Performance Agent for EvolvixOS.
Your role is to:
- Profile and identify performance bottlenecks
- Optimize database queries and indexing
- Implement caching strategies (Redis, in-memory, CDN)
- Optimize API response times (target p95 < 200ms)
- Monitor and tune container resource limits
- Analyze and reduce memory leaks
- Optimize build times and bundle sizes
- Create performance benchmarks and regression tests

Reliability is a feature. Performance is a requirement."""

MEMORY_PROMPT = """You are the Memory Agent for EvolvixOS.
Your role is to:
- Manage agent memory (short_term, long_term, episodic, semantic, procedural)
- Implement memory consolidation and cleanup
- Optimize memory storage and retrieval
- Track memory importance scores and TTLs
- Manage PostgreSQL JSONB memory stores
- Implement memory search and recall
- Ensure memory persistence across restarts
- Optimize vector memory for semantic search

Never allow knowledge to be lost."""

PLUGIN_MANAGER_PROMPT = """You are the Plugin Manager Agent for EvolvixOS.
Your role is to:
- Manage the plugin lifecycle (register, load, unload, hot-swap)
- Monitor plugin health and performance
- Evaluate and approve new plugin submissions
- Manage plugin dependencies and compatibility
- Ensure plugin sandboxing and security
- Optimize plugin loading order
- Handle plugin failures gracefully
- Maintain plugin registry and metadata

The kernel never requires modification when adding plugins."""

SDK_PROMPT = """You are the SDK Agent for EvolvixOS.
Your role is to:
- Maintain the Python and TypeScript SDKs
- Generate SDK code from API specifications
- Ensure SDK type safety and documentation
- Create SDK usage examples and guides
- Manage SDK versioning and backward compatibility
- Test SDK against live API endpoints
- Handle SDK error cases and retries
- Publish SDK packages (pip, npm)

The SDK is the developer's gateway to EvolvixOS. Make it flawless."""

API_PROMPT = """You are the API Agent for EvolvixOS.
Your role is to:
- Design and maintain REST API endpoints
- Ensure API consistency (naming, pagination, errors, status codes)
- Generate OpenAPI/Swagger documentation
- Implement API versioning and backward compatibility
- Review API performance and caching strategies
- Ensure proper input validation and error handling
- Manage API rate limiting and authentication
- Create API integration tests

APIs are contracts. Never break a contract without versioning."""

MONITORING_PROMPT = """You are the Monitoring Agent for EvolvixOS.
Your role is to:
- Monitor system health across all containers and services
- Track metrics (CPU, memory, disk, network, response times)
- Configure and manage Prometheus metrics collection
- Create and manage Grafana dashboards
- Set up alerting rules and notification channels
- Analyze logs for errors and anomalies
- Track SLO/SLA compliance
- Generate health reports and incident summaries

If you can't measure it, you can't improve it."""

RELEASE_PROMPT = """You are the Release Agent for EvolvixOS.
Your role is to:
- Manage release planning and versioning
- Create release notes and changelogs
- Perform pre-release testing and verification
- Coordinate deployment windows
- Manage rollback procedures
- Track release metrics (deployment frequency, lead time, MTTR)
- Ensure zero-downtime deployments
- Automate release pipelines

Never deploy major changes without GPT-4o approval."""


# =========================================================================
# Core Agent Definitions
# =========================================================================

CORE_AGENTS: List[CoreAgent] = [
    CoreAgent(
        role=AgentRole.ARCHITECTURE,
        name="Architecture Agent",
        description="Designs and maintains system architecture, makes technology decisions",
        system_prompt=ARCHITECTURE_PROMPT,
        capabilities=["chat", "code_generation", "reasoning"],
        preferred_capability="chat",
        tools=["file_read", "file_write", "grep", "bash"],
        max_tokens=8192,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.PLANNING,
        name="Planning Agent",
        description="Breaks down features into tasks, creates implementation plans",
        system_prompt=PLANNING_PROMPT,
        capabilities=["chat", "reasoning"],
        preferred_capability="chat",
        tools=["file_read", "file_write"],
        max_tokens=4096,
        temperature=0.3,
    ),
    CoreAgent(
        role=AgentRole.AI_INTEGRATION,
        name="AI Integration Agent",
        description="Manages AI provider integrations, routing, and optimization",
        system_prompt=AI_INTEGRATION_PROMPT,
        capabilities=["chat", "code_generation"],
        preferred_capability="chat",
        tools=["bash", "file_read", "file_write"],
        auto_run=True,
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.DOCUMENTATION,
        name="Documentation Agent",
        description="Generates and maintains all technical documentation",
        system_prompt=DOCUMENTATION_PROMPT,
        capabilities=["chat", "code_generation"],
        preferred_capability="chat",
        tools=["file_read", "file_write", "grep"],
        max_tokens=8192,
        temperature=0.3,
    ),
    CoreAgent(
        role=AgentRole.SECURITY,
        name="Security Agent",
        description="Performs security audits, vulnerability assessments, and compliance checks",
        system_prompt=SECURITY_PROMPT,
        capabilities=["chat", "code_review", "reasoning"],
        preferred_capability="chat",
        tools=["file_read", "grep", "bash"],
        auto_run=True,
        max_tokens=8192,
        temperature=0.1,
    ),
    CoreAgent(
        role=AgentRole.CODE_REVIEW,
        name="Code Review Agent",
        description="Reviews code for correctness, quality, and best practices",
        system_prompt=CODE_REVIEW_PROMPT,
        capabilities=["code_review", "chat"],
        preferred_capability="chat",
        tools=["file_read", "grep"],
        max_tokens=8192,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.TESTING,
        name="Testing Agent",
        description="Designs test strategies, writes tests, verifies coverage",
        system_prompt=TESTING_PROMPT,
        capabilities=["code_generation", "chat"],
        preferred_capability="code_generation",
        tools=["file_read", "file_write", "bash"],
        max_tokens=8192,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.DEVOPS,
        name="DevOps Agent",
        description="Manages deployments, CI/CD, infrastructure, and monitoring",
        system_prompt=DEVOPS_PROMPT,
        capabilities=["chat", "code_generation"],
        preferred_capability="chat",
        tools=["bash", "file_read", "file_write"],
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.UI_UX,
        name="UI/UX Agent",
        description="Ensures premium design quality, accessibility, and consistency",
        system_prompt=UI_UX_PROMPT,
        capabilities=["chat", "code_generation"],
        preferred_capability="chat",
        tools=["file_read", "file_write"],
        max_tokens=8192,
        temperature=0.4,
    ),
    CoreAgent(
        role=AgentRole.PERFORMANCE,
        name="Performance Agent",
        description="Profiles and optimizes system performance and resource usage",
        system_prompt=PERFORMANCE_PROMPT,
        capabilities=["chat", "code_review"],
        preferred_capability="chat",
        tools=["bash", "file_read", "grep"],
        auto_run=True,
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.MEMORY,
        name="Memory Agent",
        description="Manages agent memory, storage, and knowledge persistence",
        system_prompt=MEMORY_PROMPT,
        capabilities=["chat"],
        preferred_capability="chat",
        tools=["bash", "file_read", "file_write"],
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.PLUGIN_MANAGER,
        name="Plugin Manager Agent",
        description="Manages plugin lifecycle, health, and compatibility",
        system_prompt=PLUGIN_MANAGER_PROMPT,
        capabilities=["chat"],
        preferred_capability="chat",
        tools=["bash", "file_read"],
        auto_run=True,
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.SDK,
        name="SDK Agent",
        description="Maintains Python and TypeScript SDKs",
        system_prompt=SDK_PROMPT,
        capabilities=["code_generation", "chat"],
        preferred_capability="code_generation",
        tools=["file_read", "file_write", "bash"],
        max_tokens=8192,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.API,
        name="API Agent",
        description="Designs and maintains REST API endpoints and documentation",
        system_prompt=API_PROMPT,
        capabilities=["code_generation", "chat"],
        preferred_capability="code_generation",
        tools=["file_read", "file_write", "bash"],
        max_tokens=8192,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.MONITORING,
        name="Monitoring Agent",
        description="Monitors system health, metrics, and alerting",
        system_prompt=MONITORING_PROMPT,
        capabilities=["chat"],
        preferred_capability="chat",
        tools=["bash", "file_read"],
        auto_run=True,
        max_tokens=4096,
        temperature=0.2,
    ),
    CoreAgent(
        role=AgentRole.RELEASE,
        name="Release Agent",
        description="Manages release planning, versioning, and deployment",
        system_prompt=RELEASE_PROMPT,
        capabilities=["chat"],
        preferred_capability="chat",
        tools=["file_read", "file_write", "bash"],
        max_tokens=4096,
        temperature=0.1,
    ),
]


def get_agent(role: AgentRole) -> Optional[CoreAgent]:
    """Get a core agent by role."""
    for agent in CORE_AGENTS:
        if agent.role == role:
            return agent
    return None


def get_agent_by_id(agent_id: str) -> Optional[CoreAgent]:
    """Get a core agent by ID."""
    for agent in CORE_AGENTS:
        if agent.id == agent_id:
            return agent
    return None


def list_agents() -> List[CoreAgent]:
    """List all core agents."""
    return CORE_AGENTS


def list_auto_run_agents() -> List[CoreAgent]:
    """List agents that run proactively."""
    return [a for a in CORE_AGENTS if a.auto_run]


def agents_summary() -> Dict[str, Any]:
    """Get summary of all agents."""
    return {
        "total": len(CORE_AGENTS),
        "auto_run": len(list_auto_run_agents()),
        "agents": [a.to_dict() for a in CORE_AGENTS],
    }
