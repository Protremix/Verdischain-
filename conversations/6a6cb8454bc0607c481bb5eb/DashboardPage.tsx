import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { dashboard, ai, type AIAgent, type DashboardOverview } from '@/lib/api'
import { Activity, Cpu, Users, GitCommit, AlertCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface SubsystemHealth {
  status: string
  detail?: string
}

export function DashboardPage() {
  const { user } = useAuth()
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [agents, setAgents] = useState<AIAgent[]>([])
  const [agentHealth, setAgentHealth] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([
      dashboard.overview(),
      ai.agents(),
      ai.health(),
    ]).then(([dashResult, agentsResult, healthResult]) => {
      if (dashResult.status === 'fulfilled') setOverview(dashResult.value)
      else setError('Failed to load dashboard data')
      if (agentsResult.status === 'fulfilled') setAgents(agentsResult.value)
      if (healthResult.status === 'fulfilled') setAgentHealth(healthResult.value.agents_registered)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className='flex items-center justify-center py-20'>
        <div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' />
      </div>
    )
  }

  const subsystems = overview?.subsystems || {}
  const healthyCount = Object.values(subsystems).filter((s: SubsystemHealth) => s.status === 'healthy').length
  const totalCount = Object.keys(subsystems).length
  const agentList = agents.filter(a => a.status === 'active')
  const displayName = user?.username?.replace(/_/g, ' ') || user?.email || 'there'

  const stats = [
    { label: 'Subsystems Healthy', value: `${healthyCount}/${totalCount}`, icon: Activity, change: 'All operational', up: true },
    { label: 'AI Agents', value: String(agentHealth || agents.length), icon: Users, change: `${agentList.length} active`, up: true },
    { label: 'Registered Agents', value: String(agents.length), icon: GitCommit, change: `${agents.filter(a => a.status === 'active').length} running`, up: true },
    { label: 'System Status', value: healthyCount === totalCount ? 'Operational' : 'Degraded', icon: Cpu, change: healthyCount === totalCount ? 'All green' : 'Issues detected', up: healthyCount === totalCount },
  ]

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Dashboard</h1>
        <p className='text-sm text-text-secondary mt-1'>
          Welcome back, {displayName}. Here's what's happening across your platform.
        </p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4 flex-shrink-0' /> {error}
        </div>
      )}

      {/* Stats grid */}
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'>
        {stats.map((stat) => (
          <div key={stat.label} className='rounded-xl border border-border bg-bg-surface p-5'>
            <div className='flex items-center justify-between mb-3'>
              <div className='h-9 w-9 rounded-lg bg-brand/10 flex items-center justify-center'>
                <stat.icon className='h-4.5 w-4.5 text-brand' />
              </div>
              <span className={`text-xs flex items-center gap-0.5 ${stat.up ? 'text-emerald-400' : 'text-amber-400'}`}>
                {stat.up ? <ArrowUpRight className='h-3 w-3' /> : <ArrowDownRight className='h-3 w-3' />}
                {stat.change}
              </span>
            </div>
            <p className='text-2xl font-bold text-text-primary'>{stat.value}</p>
            <p className='text-xs text-text-tertiary mt-1'>{stat.label}</p>
          </div>
        ))}
      </div>

      <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
        {/* Subsystem health */}
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <div className='flex items-center justify-between mb-4'>
            <h2 className='text-sm font-semibold text-text-primary'>Subsystem Health</h2>
            <span className={`text-xs px-2 py-1 rounded-full ${healthyCount === totalCount ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
              {healthyCount === totalCount ? 'All Healthy' : 'Issues'}
            </span>
          </div>
          <div className='space-y-2.5'>
            {Object.entries(subsystems).slice(0, 10).map(([name, info]: [string, SubsystemHealth]) => (
              <div key={name} className='flex items-center justify-between'>
                <span className='text-sm text-text-secondary capitalize'>{name.replace(/_/g, ' ')}</span>
                <span className='flex items-center gap-2'>
                  <span className={`h-2 w-2 rounded-full ${info.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  <span className='text-xs text-text-tertiary'>{info.detail || info.status}</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Agents */}
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <div className='flex items-center justify-between mb-4'>
            <h2 className='text-sm font-semibold text-text-primary'>AI Agents</h2>
            <span className='text-xs text-text-tertiary'>{agents.length} registered</span>
          </div>
          <div className='space-y-2.5'>
            {agents.slice(0, 6).map((agent) => (
              <div key={agent.name} className='flex items-center justify-between'>
                <div>
                  <p className='text-sm text-text-primary font-medium capitalize'>{agent.display_name || agent.name.replace(/_/g, ' ')}</p>
                  <p className='text-xs text-text-tertiary'>{agent.task_types?.slice(0, 2).join(', ')}</p>
                </div>
                <div className='flex items-center gap-2'>
                  <span className='text-xs text-text-tertiary'>{agent.tasks_completed} tasks</span>
                  <span className={`h-2 w-2 rounded-full ${agent.status === 'active' ? 'bg-emerald-500' : 'bg-zinc-500'}`} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent activity from audit */}
      {overview && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <h2 className='text-sm font-semibold text-text-primary mb-4'>System Overview</h2>
          <p className='text-xs text-text-tertiary'>
            Last updated: {new Date(overview.timestamp).toLocaleString()}
          </p>
          <div className='mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3'>
            {Object.entries(subsystems).map(([name, info]: [string, SubsystemHealth]) => (
              <div key={name} className='flex items-center gap-2 text-xs'>
                <span className={`h-1.5 w-1.5 rounded-full ${info.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                <span className='text-text-secondary capitalize'>{name.replace(/_/g, ' ')}</span>
                <span className='text-text-tertiary ml-auto'>{info.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
