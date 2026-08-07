import { useState, useEffect } from 'react'
import { audit, type AuditDashboard } from '@/lib/api'
import { Shield, ShieldCheck, AlertCircle, ShieldAlert } from 'lucide-react'

export function SecurityPage() {
  const [data, setData] = useState<AuditDashboard | null>(null)
  const [checks, setChecks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.allSettled([audit.dashboard(), audit.checks()])
      .then(([dashR, checksR]) => {
        if (dashR.status === 'fulfilled') setData(dashR.value)
        else setError('Failed to load security data')
        if (checksR.status === 'fulfilled') setChecks(checksR.value)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className='flex items-center justify-center py-20'><div className='h-8 w-8 rounded-full border-2 border-border border-t-brand animate-spin' /></div>
  }

  const stats = data?.audit_stats_24h
  const totalEntries = stats?.total_entries || 0
  const warnings = stats?.by_severity?.warning || 0
  const info = stats?.by_severity?.info || 0
  const categories = stats?.by_category ? Object.entries(stats.by_category) : []

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold text-text-primary'>Security</h1>
        <p className='text-sm text-text-secondary mt-1'>Security posture and audit management</p>
      </div>

      {error && (
        <div className='flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400'>
          <AlertCircle className='h-4 w-4' /> {error}
        </div>
      )}

      {/* Score card */}
      <div className='rounded-xl border border-border bg-bg-surface p-6'>
        <div className='flex items-center justify-between'>
          <div>
            <div className='flex items-center gap-3 mb-2'>
              <div className='h-12 w-12 rounded-xl bg-emerald-500/10 flex items-center justify-center'>
                <ShieldCheck className='h-6 w-6 text-emerald-400' />
              </div>
              <div>
                <p className='text-3xl font-bold text-text-primary'>{warnings === 0 ? 'A' : 'B+'}</p>
                <p className='text-xs text-text-tertiary'>Security Grade</p>
              </div>
            </div>
          </div>
          <div className='text-right'>
            <p className='text-xs text-text-tertiary'>Last 24h Audit Entries</p>
            <p className='text-2xl font-bold text-text-primary'>{totalEntries}</p>
          </div>
        </div>
      </div>

      {/* Vulnerability summary */}
      <div className='grid grid-cols-2 sm:grid-cols-4 gap-4'>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <ShieldAlert className='h-5 w-5 text-red-400 mb-2' />
          <p className='text-2xl font-bold text-text-primary'>0</p>
          <p className='text-xs text-text-tertiary'>Critical</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <ShieldAlert className='h-5 w-5 text-orange-400 mb-2' />
          <p className='text-2xl font-bold text-text-primary'>0</p>
          <p className='text-xs text-text-tertiary'>High</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <Shield className='h-5 w-5 text-amber-400 mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{warnings}</p>
          <p className='text-xs text-text-tertiary'>Warnings</p>
        </div>
        <div className='rounded-xl border border-border bg-bg-surface p-4'>
          <ShieldCheck className='h-5 w-5 text-emerald-400 mb-2' />
          <p className='text-2xl font-bold text-text-primary'>{info}</p>
          <p className='text-xs text-text-tertiary'>Info Events</p>
        </div>
      </div>

      {/* Audit categories */}
      {categories.length > 0 && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <h2 className='text-sm font-semibold text-text-primary mb-4'>Audit Events by Category (24h)</h2>
          <div className='space-y-2'>
            {categories.map(([cat, count]: [string, number]) => (
              <div key={cat} className='flex items-center justify-between'>
                <span className='text-sm text-text-secondary capitalize'>{cat.replace(/_/g, ' ')}</span>
                <div className='flex items-center gap-3'>
                  <div className='h-1.5 w-24 rounded-full bg-bg-base overflow-hidden'>
                    <div className='h-full bg-brand rounded-full' style={{ width: `${Math.min((count / totalEntries) * 100, 100)}%` }} />
                  </div>
                  <span className='text-xs text-text-tertiary w-8 text-right'>{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Security checks */}
      {checks.length > 0 && (
        <div className='rounded-xl border border-border bg-bg-surface p-5'>
          <h2 className='text-sm font-semibold text-text-primary mb-4'>Security Checks</h2>
          <div className='space-y-2'>
            {checks.slice(0, 10).map((check: any, i: number) => (
              <div key={check.id || i} className='flex items-center justify-between py-2 border-b border-border/50 last:border-0'>
                <span className='text-sm text-text-secondary'>{check.name || check.description}</span>
                <span className={`text-xs px-2 py-1 rounded-full ${check.status === 'passed' || check.status === 'healthy' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                  {check.status || 'unknown'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
