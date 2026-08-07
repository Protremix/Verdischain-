import { useState, useEffect } from 'react'
import { ai, type AIAgent, type AIHealth } from '@/lib/api'
import { Activity, AlertCircle } from 'lucide-react'

export function AIWorkspacePage() {
  const [agents, setAgents] = useState<AIAgent[]>([])
  const [health, setHealth] = useState<AIHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([ai.agents(), ai.health()])
      .then(([agentsR, healthR]) => {
        if (agentsR.status === 'fulfilled') setAgents(agentsR.value)
        else setError('Failed to load AI agents')
        if (healthR.status === 'fulfilled') setHealth(healthR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  const activeAgents = agents.filter(a => a.status === 'active')

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>AI Workspace</h1>
        <p className='text-sm text-text-secondary mt-1'>Intelligent engineering assistance</p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Health banner */}
      {health && (
        <div className='flex items-center justify-between rounded-xl border border-border bg-bg-surface p-4'>
          <div className='flex items-center gap-3'>
            <span className={`h-3 w-3 rounded-full ${health.status === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span className='text-sm font-medium text-text-primary'>{health.agents_registered} agents online</span>
          </div>
          <div className='flex items-center gap-4 text-xs text-text-tertiary'>
            <span>Model: {health.llm_model}</span>
            <span>API Key: {health.llm_api_key_configured ? '✓' : '✗'}</span>
          </div>
        </div>
      )}

      {/* Agent grid */}
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'>
        {agents.map((agent) => (
          <div key={agent.name} className='rounded-xl border border-border bg-bg-surface p-5'>
            <div className='flex items-start justify-between mb-3'>
              <div className='h-10 w-10 rounded-lg bg-brand/10 flex items-center justify-center'>
                <Activity className='h-5 w-5 text-brand' />
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${agent.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-500/10 text-zinc-400'}`}>
                {agent.status}
              </span>
            </div>
            <h3 className='text-sm font-semibold text-text-primary capitalize'>{agent.display_name || agent.name.replace(/_/g, ' ')}</h3>
            <p className='text-xs text-text-tertiary mt-1 line-clamp-2'>{agent.description}</p>
            <div className='mt-3 flex flex-wrap gap-1.5'>
              {agent.task_types?.map((t) => (
                <span key={t} className='text-xs px-2 py-0.5 rounded bg-bg-base text-text-tertiary border border-border'>{t.replace(/_/g, ' ')}</span>
              ))}
            </div>
            <div className='mt-3 flex items-center justify-between text-xs text-text-tertiary'>
              <span>{agent.model}</span>
              <span>{agent.tasks_completed} tasks</span>
            </div>
          </div>
        ))}
      </div>

      {agents.length === 0 && !error && (
        <div className='text-center py-12 text-text-tertiary'>
          <p className='text-sm'>No AI agents registered.</p>
        </div>
      )}
    </div>
  )
}
