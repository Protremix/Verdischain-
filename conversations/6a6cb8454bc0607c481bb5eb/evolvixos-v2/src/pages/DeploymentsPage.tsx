import { Rocket, GitBranch, CheckCircle2, Clock, XCircle, ArrowUpRight } from 'lucide-react'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

const deployments = [
  { name: 'EvolvixOS API', version: 'v2.0.0', env: 'production', status: 'success', time: '2 min ago', duration: '1m 42s' },
  { name: 'Verdis Node', version: 'v1.8.0', env: 'production', status: 'success', time: '1h ago', duration: '3m 12s' },
  { name: 'Frontend', version: 'v2.0.0', env: 'staging', status: 'success', time: '2h ago', duration: '45s' },
  { name: 'Customer Success', version: 'v1.2.0', env: 'production', status: 'success', time: '4h ago', duration: '1m 03s' },
  { name: 'Grafana Alerts', version: 'v1.0.0', env: 'production', status: 'success', time: '8h ago', duration: '12s' },
  { name: 'Log Aggregation', version: 'v1.0.0', env: 'production', status: 'failed', time: '1d ago', duration: '2m 34s' },
]

const statusMap = {
  success: { icon: CheckCircle2, variant: 'success' as const, label: 'Deployed' },
  pending: { icon: Clock, variant: 'warning' as const, label: 'In Progress' },
  failed: { icon: XCircle, variant: 'danger' as const, label: 'Failed' },
}

export function DeploymentsPage() {
  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Deployments</h1>
        <p className="mt-1 text-sm text-text-secondary">Deployment history and pipeline status</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card padding="md">
          <p className="text-xs text-text-tertiary font-medium">Success Rate</p>
          <p className="mt-2 text-3xl font-semibold text-text-primary tabular-nums">94%</p>
          <div className="mt-2 flex items-center gap-1">
            <Badge variant="success" dot>142 / 151</Badge>
          </div>
        </Card>
        <Card padding="md">
          <p className="text-xs text-text-tertiary font-medium">Avg Duration</p>
          <p className="mt-2 text-3xl font-semibold text-text-primary tabular-nums">1m 28s</p>
          <p className="mt-1 text-xs text-success">↓ 12% faster</p>
        </Card>
        <Card padding="md">
          <p className="text-xs text-text-tertiary font-medium">This Week</p>
          <p className="mt-2 text-3xl font-semibold text-text-primary tabular-nums">23</p>
          <p className="mt-1 text-xs text-text-tertiary">deployments</p>
        </Card>
      </div>

      <Card padding="none" className="overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <CardTitle>Recent Deployments</CardTitle>
        </div>
        <div className="divide-y divide-border">
          {deployments.map((d, i) => {
            const status = statusMap[d.status as keyof typeof statusMap]
            return (
              <div key={i} className="flex items-center gap-4 px-6 py-4 hover:bg-bg-hover transition-colors">
                <div className={`h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0
                  ${d.status === 'success' ? 'bg-success/10' : 'bg-danger/10'}`}>
                  <status.icon className={`h-4.5 w-4.5 ${d.status === 'success' ? 'text-success' : 'text-danger'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-text-primary">{d.name}</p>
                    <Badge variant={d.env === 'production' ? 'brand' : 'default'}>{d.env}</Badge>
                  </div>
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-text-tertiary">
                    <span className="flex items-center gap-1"><GitBranch className="h-3 w-3" />{d.version}</span>
                    <span>·</span>
                    <span>{d.duration}</span>
                    <span>·</span>
                    <span>{d.time}</span>
                  </div>
                </div>
                <Badge variant={status.variant} dot>{status.label}</Badge>
                <button className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-bg-hover transition-colors text-text-tertiary hover:text-text-primary">
                  <ArrowUpRight className="h-4 w-4" />
                </button>
              </div>
            )
          })}
        </div>
      </Card>
    </div>
  )
}
