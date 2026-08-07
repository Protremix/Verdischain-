import { useState, useEffect } from 'react'
import { deploy, type DeployDashboard, type DeploymentEnv } from '@/lib/api'
import { Rocket, Server, Globe, Lock, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react'

export function DeploymentsPage() {
  const [dashData, setDashData] = useState<DeployDashboard | null>(null)
  const [envs, setEnvs] = useState<DeploymentEnv[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([deploy.dashboard(), deploy.environments()])
      .then(([dashR, envsR]) => {
        if (dashR.status === 'fulfilled') setDashData(dashR.value)
        else setError('Failed to load deployment data')
        if (envsR.status === 'fulfilled') setEnvs(envsR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  const stats = dashData?.stats
  const progress = dashData?.progress

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Deployments</h1>
        <p className='text-sm text-text-secondary mt-1'>Deployment history and pipeline status</p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Stats */}
      <div className='grid grid-cols-2 lg:grid-cols-4 gap-4'>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <Rocket className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{stats?.total_scripts || 0}</p>
          <p className='text-xs text-text-tertiary'>Deploy Scripts</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <Globe className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{stats?.total_dns_records || 0}</p>
          <p className='text-xs text-text-tertiary'>DNS Records</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <Lock className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{stats?.total_ssl_configs || 0}</p>
          <p className='text-xs text-text-tertiary'>SSL Certificates</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <Server className='h-5 w-5 text-brand mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{progress ? `${progress.completed}/${progress.total}` : '0/0'}</p>
          <p className='text-xs text-text-tertiary'>Deployment Steps</p>
        </div>
      </div>

      {/* Deployment progress */}
      {progress && progress.total > 0 && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <div className='flex items-center justify-between mb-3'>
            <h2 className='text-sm font-semibold text-text-primary'>Deployment Progress</h2>
            <span className='text-xs text-text-tertiary'>{progress.percentage.toFixed(1)}% complete</span>
          </div>
          <div className='h-2 rounded-full bg-bg-base overflow-hidden mb-4'>
            <div className='h-full bg-brand rounded-full transition-all' style={{ width: `${progress.percentage}%` }} />
          </div>
          {progress.next_step && (
            <div className='flex items-center gap-2 text-xs text-text-tertiary'>
              <Clock className='h-3.5 w-3.5' />
              <span>Next: {progress.next_step.name} — {progress.next_step.description}</span>
            </div>
          )}
        </div>
      )}

      {/* Environments */}
      {envs.length > 0 && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <h2 className='text-sm font-semibold text-text-primary mb-4'>Environments</h2>
          <div className='space-y-4'>
            {envs.map((env) => (
              <div key={env.target} className='border border-border rounded-lg p-4'>
                <div className='flex items-center justify-between mb-3'>
                  <div>
                    <h3 className='text-sm font-medium text-text-primary'>{env.name}</h3>
                    <p className='text-xs text-text-tertiary'>{env.url}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${env.status === 'online' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-500/10 text-zinc-400'}`}>
                    {env.status}
                  </span>
                </div>
                <div className='grid grid-cols-2 sm:grid-cols-3 gap-2'>
                  {Object.entries(env.components).map(([comp, status]) => (
                    <div key={comp} className='flex items-center gap-1.5 text-xs'>
                      {status === 'deployed' || status === 'healthy' ? (
                        <CheckCircle className='h-3.5 w-3.5 text-emerald-400' />
                      ) : status === 'failed' || status === 'error' ? (
                        <XCircle className='h-3.5 w-3.5 text-red-400' />
                      ) : (
                        <Clock className='h-3.5 w-3.5 text-zinc-400' />
                      )}
                      <span className='text-text-tertiary capitalize'>{comp.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
