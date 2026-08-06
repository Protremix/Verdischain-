import {
  FolderGit2, Bot, GitCommit, Users, TrendingUp, TrendingDown,
  Cpu, HardDrive, Activity, AlertCircle, CheckCircle2, Clock,
  ArrowUpRight, Sparkles
} from 'lucide-react'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Progress } from '@/components/ui/Progress'
import { cn } from '@/lib/cn'

const stats = [
  { label: 'Active Projects', value: '12', change: '+2', trend: 'up', icon: FolderGit2 },
  { label: 'AI Agents', value: '5', change: '+1', trend: 'up', icon: Bot },
  { label: 'Commits / Week', value: '847', change: '+12%', trend: 'up', icon: GitCommit },
  { label: 'Team Members', value: '24', change: '0', trend: 'neutral', icon: Users },
]

const recentActivity = [
  { type: 'deploy', title: 'EvolvixOS API deployed to production', meta: 'v2.0.0 · 2 min ago', status: 'success' },
  { type: 'ai', title: 'AI Architect completed code review', meta: 'Verdis Chain · 8 min ago', status: 'info' },
  { type: 'commit', title: 'New commit: feat: add GRANDPA finality', meta: 'verdis-chain · 23 min ago', status: 'default' },
  { type: 'alert', title: 'High CPU usage detected on node-3', meta: 'Monitoring · 1 hour ago', status: 'warning' },
  { type: 'deploy', title: 'Frontend build completed', meta: 'evolvixos-frontend · 2 hours ago', status: 'success' },
  { type: 'ai', title: 'AI Planner generated roadmap Q3 2026', meta: 'EvolvixOS · 3 hours ago', status: 'info' },
]

const systemMetrics = [
  { label: 'CPU Usage', value: 42, color: 'brand' as const, detail: '42% · 8 cores' },
  { label: 'Memory', value: 63, color: 'warning' as const, detail: '10.1 / 16 GB' },
  { label: 'Disk', value: 28, color: 'success' as const, detail: '1.4 / 5 TB' },
  { label: 'Network I/O', value: 15, color: 'brand' as const, detail: '2.3 MB/s' },
]

const aiAgents = [
  { name: 'AI CTO', role: 'Architecture & Strategy', status: 'active', tasks: 47 },
  { name: 'AI Architect', role: 'Code Review & Design', status: 'active', tasks: 23 },
  { name: 'AI Planner', role: 'Roadmaps & Sprints', status: 'idle', tasks: 8 },
  { name: 'AI Reviewer', role: 'Security & Quality', status: 'active', tasks: 15 },
  { name: 'AI Developer', role: 'Code Generation', status: 'active', tasks: 62 },
]

const statusColors = {
  success: 'success' as const,
  info: 'brand' as const,
  warning: 'warning' as const,
  danger: 'danger' as const,
  default: 'default' as const,
}

export function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          Welcome back, Rojs. Here's what's happening across your projects.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(stat => (
          <Card key={stat.label} hover padding="md">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-text-secondary">{stat.label}</p>
                <p className="mt-2 text-3xl font-semibold text-text-primary tabular-nums">{stat.value}</p>
                {stat.change !== '0' && (
                  <div className="mt-1.5 flex items-center gap-1">
                    {stat.trend === 'up' ? (
                      <TrendingUp className="h-3.5 w-3.5 text-success" />
                    ) : (
                      <TrendingDown className="h-3.5 w-3.5 text-danger" />
                    )}
                    <span className={cn('text-xs font-medium', stat.trend === 'up' ? 'text-success' : 'text-danger')}>
                      {stat.change}
                    </span>
                    <span className="text-xs text-text-tertiary">vs last week</span>
                  </div>
                )}
              </div>
              <div className="h-10 w-10 rounded-lg bg-bg-hover flex items-center justify-center">
                <stat.icon className="h-5 w-5 text-text-secondary" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent Activity */}
        <Card className="lg:col-span-2" padding="md">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <button className="text-xs font-medium text-brand hover:text-brand-hover flex items-center gap-1">
              View all <ArrowUpRight className="h-3 w-3" />
            </button>
          </CardHeader>
          <div className="space-y-1">
            {recentActivity.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg p-2.5 hover:bg-bg-hover transition-colors group"
              >
                <div className={cn(
                  'h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0',
                  item.status === 'success' && 'bg-success/10',
                  item.status === 'info' && 'bg-brand/10',
                  item.status === 'warning' && 'bg-warning/10',
                  item.status === 'default' && 'bg-bg-hover',
                )}>
                  {item.status === 'success' && <CheckCircle2 className="h-4 w-4 text-success" />}
                  {item.status === 'info' && <Sparkles className="h-4 w-4 text-brand" />}
                  {item.status === 'warning' && <AlertCircle className="h-4 w-4 text-warning" />}
                  {item.status === 'default' && <GitCommit className="h-4 w-4 text-text-tertiary" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary truncate">{item.title}</p>
                  <p className="text-xs text-text-tertiary">{item.meta}</p>
                </div>
                <Badge variant={statusColors[item.status as keyof typeof statusColors]} dot>
                  {item.type}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        {/* System Metrics */}
        <Card padding="md">
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <Badge variant="success" dot>Operational</Badge>
          </CardHeader>
          <div className="space-y-4">
            {systemMetrics.map(metric => (
              <div key={metric.label}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {metric.label === 'CPU Usage' && <Cpu className="h-3.5 w-3.5 text-text-tertiary" />}
                    {metric.label === 'Memory' && <HardDrive className="h-3.5 w-3.5 text-text-tertiary" />}
                    {metric.label === 'Disk' && <HardDrive className="h-3.5 w-3.5 text-text-tertiary" />}
                    {metric.label === 'Network I/O' && <Activity className="h-3.5 w-3.5 text-text-tertiary" />}
                    <span className="text-sm text-text-secondary">{metric.label}</span>
                  </div>
                  <span className="text-xs text-text-tertiary tabular-nums">{metric.detail}</span>
                </div>
                <Progress value={metric.value} color={metric.color} size="sm" />
              </div>
            ))}
          </div>
          <div className="mt-6 pt-4 border-t border-border">
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-secondary">Uptime</span>
              <span className="font-medium text-text-primary tabular-nums">99.98%</span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-text-secondary">Avg Response</span>
              <span className="font-medium text-text-primary tabular-nums">42ms</span>
            </div>
          </div>
        </Card>
      </div>

      {/* AI Agents */}
      <Card padding="md">
        <CardHeader>
          <CardTitle>AI Agents</CardTitle>
          <button className="text-xs font-medium text-brand hover:text-brand-hover flex items-center gap-1">
            Manage <ArrowUpRight className="h-3 w-3" />
          </button>
        </CardHeader>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {aiAgents.map(agent => (
            <div
              key={agent.name}
              className="rounded-lg border border-border bg-bg-surface p-4 card-hover"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="h-9 w-9 rounded-lg bg-brand-gradient flex items-center justify-center">
                  <Bot className="h-4.5 w-4.5 text-white" />
                </div>
                <Badge variant={agent.status === 'active' ? 'success' : 'default'} dot>
                  {agent.status}
                </Badge>
              </div>
              <p className="text-sm font-semibold text-text-primary">{agent.name}</p>
              <p className="text-xs text-text-tertiary mt-0.5">{agent.role}</p>
              <div className="mt-3 flex items-center gap-1.5 text-xs text-text-secondary">
                <Clock className="h-3.5 w-3.5" />
                <span className="tabular-nums">{agent.tasks} tasks this week</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
