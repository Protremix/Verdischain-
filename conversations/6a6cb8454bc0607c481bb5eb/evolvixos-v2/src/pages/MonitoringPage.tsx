import { Activity, Cpu, HardDrive, Network, Zap, Server, AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { LineChart, Line, AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

const cpuData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}h`,
  cpu: 30 + Math.sin(i / 3) * 20 + Math.random() * 10,
  memory: 55 + Math.cos(i / 4) * 15 + Math.random() * 5,
}))

const networkData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}h`,
  inbound: Math.random() * 5 + 1,
  outbound: Math.random() * 3 + 0.5,
}))

const services = [
  { name: 'Frontend', status: 'healthy', latency: '12ms', uptime: '99.99%' },
  { name: 'API Gateway', status: 'healthy', latency: '42ms', uptime: '99.98%' },
  { name: 'Verdis Node', status: 'healthy', latency: '8ms', uptime: '100%' },
  { name: 'Customer Success', status: 'healthy', latency: '156ms', uptime: '99.95%' },
  { name: 'PostgreSQL', status: 'healthy', latency: '3ms', uptime: '99.99%' },
  { name: 'Redis', status: 'healthy', latency: '1ms', uptime: '100%' },
  { name: 'Prometheus', status: 'healthy', latency: '15ms', uptime: '99.97%' },
  { name: 'Grafana', status: 'healthy', latency: '22ms', uptime: '99.97%' },
]

export function MonitoringPage() {
  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary">Monitoring</h1>
        <p className="mt-1 text-sm text-text-secondary">Real-time system health and performance metrics</p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'CPU Usage', value: '42%', icon: Cpu, trend: '12% avg', color: 'text-brand' },
          { label: 'Memory', value: '63%', icon: HardDrive, trend: '10.1/16 GB', color: 'text-warning' },
          { label: 'Network I/O', value: '2.3 MB/s', icon: Network, trend: '↑ 15%', color: 'text-success' },
          { label: 'Block Height', value: '10,206', icon: Zap, trend: '5s block time', color: 'text-info' },
        ].map(m => (
          <Card key={m.label} padding="md">
            <div className="flex items-center justify-between mb-3">
              <m.icon className="h-5 w-5 text-text-tertiary" />
              <Badge variant="success" dot>Live</Badge>
            </div>
            <p className="text-2xl font-semibold text-text-primary tabular-nums">{m.value}</p>
            <p className="text-xs text-text-tertiary mt-1">{m.label}</p>
            <p className={m.color + ' text-xs font-medium mt-1'}>{m.trend}</p>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card padding="md">
          <CardHeader>
            <div>
              <CardTitle>CPU & Memory</CardTitle>
              <CardDescription>Last 24 hours</CardDescription>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" />CPU</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-warning" />Memory</span>
            </div>
          </CardHeader>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={cpuData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border-subtle))" vertical={false} />
              <XAxis dataKey="time" stroke="rgb(var(--text-tertiary))" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="rgb(var(--text-tertiary))" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  background: 'rgb(var(--bg-elevated))',
                  border: '1px solid rgb(var(--border-base))',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                labelStyle={{ color: 'rgb(var(--text-secondary))' }}
              />
              <Line type="monotone" dataKey="cpu" stroke="rgb(var(--brand))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="memory" stroke="rgb(var(--warning))" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card padding="md">
          <CardHeader>
            <div>
              <CardTitle>Network Traffic</CardTitle>
              <CardDescription>Last 24 hours · MB/s</CardDescription>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" />Inbound</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-info" />Outbound</span>
            </div>
          </CardHeader>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={networkData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--border-subtle))" vertical={false} />
              <XAxis dataKey="time" stroke="rgb(var(--text-tertiary))" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="rgb(var(--text-tertiary))" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  background: 'rgb(var(--bg-elevated))',
                  border: '1px solid rgb(var(--border-base))',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                labelStyle={{ color: 'rgb(var(--text-secondary))' }}
              />
              <Area type="monotone" dataKey="inbound" stroke="rgb(var(--success))" fill="rgb(var(--success) / 0.1)" strokeWidth={2} />
              <Area type="monotone" dataKey="outbound" stroke="rgb(var(--info))" fill="rgb(var(--info) / 0.1)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Service status */}
      <Card padding="md">
        <CardHeader>
          <CardTitle>Service Status</CardTitle>
          <Badge variant="success" dot>All Healthy</Badge>
        </CardHeader>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {services.map(s => (
            <div key={s.name} className="rounded-lg border border-border bg-bg-surface p-3.5">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Server className="h-4 w-4 text-text-tertiary" />
                  <span className="text-sm font-medium text-text-primary">{s.name}</span>
                </div>
                <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
              </div>
              <div className="flex items-center justify-between text-xs text-text-tertiary">
                <span>{s.latency}</span>
                <span>{s.uptime}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
