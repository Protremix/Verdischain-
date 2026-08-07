/**
 * EvolvixOS API Client
 * Centralized fetch wrapper with JWT auth, error handling, and typed endpoints.
 */

const API_BASE = '/api/v1'

function getToken(): string | null {
  return localStorage.getItem('evolvixos_token')
}

export function setToken(token: string) {
  localStorage.setItem('evolvixos_token', token)
}

export function clearToken() {
  localStorage.removeItem('evolvixos_token')
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (resp.status === 401) {
    clearToken()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || error.error?.message || `HTTP ${resp.status}`)
  }

  return resp.json()
}

// ===== Auth =====
export interface User {
  id: string
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export const auth = {
  register: (data: { full_name: string; email: string; password: string }) =>
    apiFetch<User>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  login: (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('email', email)
    formData.append('password', password)
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    }).then(async r => {
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || 'Login failed')
      return r.json() as Promise<AuthTokens>
    })
  },

  me: () => apiFetch<User>('/auth/me'),
}

// ===== Dashboard =====
export interface DashboardOverview {
  timestamp: string
  subsystems: Record<string, { status: string; detail?: string; [k: string]: unknown }>
}

export const dashboard = {
  overview: () => apiFetch<DashboardOverview>('/dashboard/overview'),
}

// ===== AI =====
export interface AIAgent {
  name: string
  description: string
  task_types: string[]
  display_name: string
  status: string
  model: string
  tasks_completed: number
}

export interface AIHealth {
  status: string
  agents_registered: number
  agents: string[]
  llm_model: string
  llm_api_key_configured: boolean
}

export const ai = {
  agents: () => apiFetch<AIAgent[]>('/ai/agents'),
  health: () => apiFetch<AIHealth>('/ai/health'),
}

// ===== Audit / Security =====
export interface AuditDashboard {
  audit_stats_24h: {
    total_entries: number
    by_category: Record<string, number>
    by_severity: Record<string, number>
    by_actor: Record<string, number>
  }
  [k: string]: unknown
}

export const audit = {
  dashboard: () => apiFetch<AuditDashboard>('/audit/dashboard'),
  checks: () => apiFetch<any[]>('/audit/checks'),
}

// ===== Deployment =====
export interface DeployDashboard {
  stats: {
    total_scripts: number
    total_dns_records: number
    total_ssl_configs: number
    total_steps: number
    completed_steps: number
    pending_steps: number
  }
  progress: {
    total: number
    completed: number
    pending: number
    percentage: number
    next_step?: { id: string; name: string; description: string }
  }
}

export interface DeploymentEnv {
  name: string
  target: string
  url: string
  status: string
  components: Record<string, string>
  last_deploy: string
  version: string
  uptime_percent: number
}

export const deploy = {
  dashboard: () => apiFetch<DeployDashboard>('/deploy/dashboard'),
  environments: () => apiFetch<DeploymentEnv[]>('/deployment/environments'),
}

// ===== Projects =====
export interface Project {
  id: string
  name: string
  type: string
  status: string
  description: string
  repository: string
  domain: string
  health_endpoint: string
  config: Record<string, any>
  tags: string[]
  created_at: string
  updated_at: string
  health_status: string
}

export interface ProjectStats {
  total_projects: number
  active: number
  paused: number
  archived: number
  by_type: Record<string, number>
  by_status: Record<string, number>
}

export const projects = {
  list: () => apiFetch<Project[]>('/multi-project/projects'),
  stats: () => apiFetch<ProjectStats>('/multi-project/stats'),
}

// ===== Knowledge Base =====
export interface KnowledgeEntry {
  id: string
  category: string
  title: string
  content: string
  source: string
  tags: string[]
  confidence: number
  times_referenced: number
  created_at: string
  updated_at: string
}

export interface KnowledgeStats {
  total_entries: number
  total_patterns: number
  categories: Record<string, number>
  sources: Record<string, number>
  total_references: number
  avg_confidence: number
}

export interface DocsDashboard {
  stats: {
    total_docs: number
    total_manifests: number
    total_faqs: number
    total_runbooks: number
    total_words: number
    published_docs: number
    doc_categories: number
  }
  recent_docs: Array<{
    id: string
    title: string
    category: string
    description: string
    status: string
    author: string
    tags: string[]
    created: string
    updated: string
    word_count: number
  }>
}

export const knowledge = {
  list: () => apiFetch<KnowledgeEntry[]>('/knowledge-base/'),
  stats: () => apiFetch<KnowledgeStats>('/knowledge-base/stats'),
  docsDashboard: () => apiFetch<DocsDashboard>('/docs/dashboard'),
}
