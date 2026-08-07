import { useState, useEffect } from 'react'
import { dashboard, ai, type DashboardOverview } from '@/lib/api'
import { Cpu, MemoryStick, HardDrive, Network, AlertCircle } from 'lucide-react'

export function MonitoringPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [agentHealth, setAgentHealth] = useState<{ agents_registered: number; status: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([dashboard.overview(), ai.health()])
      .then(([dashR, healthR]) => {
        if (dashR.status === 'fulfilled') setOverview(dashR.value)
        else setError('Failed to load monitoring data')
        if (healthR.status === 'fulfilled') setAgentHealth(healthR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  const subsystems = overview?.subsystems || {}
  const entries = Object.entries(subsystems)
  const healthy = entries.filter(([, v]) => (v as any).status === 'healthy').length

  const stats = [
    { label: 'Subsystems', value: `${healthy}/${entries.length}`, icon: Cpu, healthy },
    { label: 'AI Agents', value: String(agentHealth?.agents_registered || 0), icon: Network, healthy: true },
    { label: 'AI Status', value: agentHealth?.status || 'unknown', icon: MemoryStick, healthy: agentHealth?.status === 'healthy' },
    { label: 'Overall', value: healthy === entries.length ? 'Operational' : 'Degraded', icon: HardDrive, healthy: healthy === entries.length },
  ]

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-2xl font-bold text-text-primary'>Monitoring</h1>
          <p className='text-sm text-text-secondary mt-1'>Real-time system health and performance metrics</p>
        </div>
        <span className='flex items-center gap-2 text-xs px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-400'>
          <span className='h-2 w-2 rounded-full bg-emerald-500 animate-pulse' /> Live
        </span>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Stats grid */}
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4'>
        {stats.map((stat) => (
          <div key={stat.label} className='rounded-xl border border-border bg-bg-surface p-5'>
            <div className='flex items-center justify-between mb-3'>
              <div className={`h-9 w-9 rounded-lg flex items-center justify-center ${stat.healthy ? 'bg-emerald-500/10' : 'bg-amber-500/10'}`}>
                <stat.icon className={`h-4.5 w-4.5 ${stat.healthy ? 'text-emerald-400' : 'text-amber-400'}`} />
              </div>
              <span className='flex items-center gap-1.5 text-xs text-text-tertiary'>
                <span className={`h-2 w-2 rounded-full ${stat.healthy ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse`} /> Live
              </span>
            </div>
            <p className='text-2xl font-bold text-text-primary capitalize'>{stat.value}</p>
            <p className='text-xs text-text-tertiary mt-1'>{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Service status table */}
      <div className='rounded-xl border border-border bg-bg-surface p-5'>
        <h2 className='text-sm font-semibold text-text-primary mb-4'>Service Status</h2>
        {entries.length === 0 ? (
          <p className='text-sm text-text-tertiary text-center py-6'>No service data available</p>
        ) : (
          <div className='space-y-2'>
            {entries.map(([name, info]: [string, any]) => (
              <div key={name} className='flex items-center justify-between py-2 border-b border-border/50 last:border-0'>
                <span className='text-sm text-text-secondary capitalize'>{name.replace(/_/g, ' ')}</span>
                <div className='flex items-center gap-3'>
                  <span className='text-xs text-text-tertiary'>{info.detail || '—'}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${info.status === 'healthy' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                    {info.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
