import { Shield, Lock, KeyRound, AlertTriangle, CheckCircle2, FileWarning } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'

const securityChecks = [
  { name: 'SSL/TLS Certificate', status: 'pass', detail: 'Valid until Nov 2026' },
  { name: 'Rate Limiting', status: 'pass', detail: '4 zones configured' },
  { name: 'CORS Policy', status: 'pass', detail: '7 origins allowlisted' },
  { name: 'JWT Authentication', status: 'pass', detail: '1h expiry + 7d refresh' },
  { name: 'Account Lockout', status: 'pass', detail: '5 attempts / 15min' },
  { name: 'Security Headers', status: 'pass', detail: 'All 7 headers active' },
  { name: 'Backup System', status: 'pass', detail: 'Restic · 3am UTC daily' },
  { name: 'Log Aggregation', status: 'pass', detail: 'Loki · 7-day retention' },
]

const vulnerabilities = [
  { severity: 'critical', count: 0 },
  { severity: 'high', count: 0 },
  { severity: 'medium', count: 2 },
  { severity: 'low', count: 3 },
]

export function SecurityPage() {
  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Security</h1>
        <p className="mt-1 text-sm text-text-secondary">Security posture and vulnerability management</p>
      </div>

      {/* Score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card padding="lg" className="lg:col-span-1">
          <div className="flex items-center justify-between mb-4">
            <div className="h-12 w-12 rounded-xl bg-success/10 flex items-center justify-center">
              <Shield className="h-6 w-6 text-success" />
            </div>
            <Badge variant="success" dot>A</Badge>
          </div>
          <p className="text-4xl font-semibold text-text-primary tabular-nums">92<span className="text-2xl text-text-tertiary">/100</span></p>
          <p className="text-sm text-text-secondary mt-1">Security Score</p>
          <div className="mt-4">
            <Progress value={92} color="success" />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-text-tertiary">Last Audit</p>
              <p className="text-sm font-medium text-text-primary">Aug 5, 2026</p>
            </div>
            <div>
              <p className="text-xs text-text-tertiary">Next Scan</p>
              <p className="text-sm font-medium text-text-primary">Aug 12, 2026</p>
            </div>
          </div>
        </Card>

        {/* Vulnerabilities */}
        <Card padding="md" className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Vulnerability Summary</CardTitle>
            <Badge variant="success" dot>No Critical Issues</Badge>
          </CardHeader>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {vulnerabilities.map(v => (
              <div key={v.severity} className="rounded-lg border border-border bg-bg-surface p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-text-tertiary">{v.severity}</p>
                <p className="mt-2 text-3xl font-semibold text-text-primary tabular-nums">{v.count}</p>
                {v.count === 0 && <CheckCircle2 className="mt-1 h-4 w-4 text-success" />}
                {v.count > 0 && <AlertTriangle className={v.severity === 'medium' ? 'mt-1 h-4 w-4 text-warning' : 'mt-1 h-4 w-4 text-info'} />}
              </div>
            ))}
          </div>
          <div className="mt-4 space-y-2">
            <div className="flex items-center gap-3 rounded-lg p-2.5 bg-warning/5 border border-warning/20">
              <FileWarning className="h-4 w-4 text-warning flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary">WebSocket authentication not enforced</p>
                <p className="text-xs text-text-tertiary">Medium · evolvixos-api</p>
              </div>
              <Badge variant="warning">Medium</Badge>
            </div>
            <div className="flex items-center gap-3 rounded-lg p-2.5 bg-warning/5 border border-warning/20">
              <FileWarning className="h-4 w-4 text-warning flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary">Duplicate detection scaling concern</p>
                <p className="text-xs text-text-tertiary">Medium · customer-success</p>
              </div>
              <Badge variant="warning">Medium</Badge>
            </div>
          </div>
        </Card>
      </div>

      {/* Security checks */}
      <Card padding="md">
        <CardHeader>
          <CardTitle>Security Checks</CardTitle>
          <span className="text-xs text-text-tertiary">{securityChecks.length} checks · all passing</span>
        </CardHeader>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {securityChecks.map(check => (
            <div key={check.name} className="flex items-center gap-3 rounded-lg p-3 bg-bg-surface border border-border">
              <CheckCircle2 className="h-4.5 w-4.5 text-success flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary">{check.name}</p>
                <p className="text-xs text-text-tertiary">{check.detail}</p>
              </div>
              <Lock className="h-3.5 w-3.5 text-text-tertiary" />
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
