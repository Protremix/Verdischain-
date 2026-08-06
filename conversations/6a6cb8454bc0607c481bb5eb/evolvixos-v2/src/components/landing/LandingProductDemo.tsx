import { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/cn'
import { Reveal } from './Reveal'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { Cpu, Bot, Shield, GitBranch, Zap, CheckCircle2, Activity, Terminal, Rocket } from 'lucide-react'

/* ==================== PANEL 1: AI Agents Activity Feed ==================== */

const activityItems = [
  { icon: Cpu, name: 'AI CTO', action: 'Analyzing architecture patterns...', result: 'Security score: 8.5/10', color: 'text-blue-400' },
  { icon: Shield, name: 'AI Reviewer', action: 'Scanning codebase for vulnerabilities...', result: '0 critical, 2 medium findings', color: 'text-amber-400' },
  { icon: GitBranch, name: 'AI Planner', action: 'Generating Q3 roadmap...', result: '12 epics, 47 stories', color: 'text-purple-400' },
  { icon: Zap, name: 'AI Developer', action: 'Refactoring authentication module...', result: '23 files updated', color: 'text-emerald-400' },
  { icon: Bot, name: 'AI Architect', action: 'Reviewing API design...', result: '3 improvements recommended', color: 'text-indigo-400' },
]

function ActivityFeed() {
  const { ref, isVisible } = useScrollReveal<HTMLDivElement>({ threshold: 0.2 })
  const [visibleCount, setVisibleCount] = useState(0)

  useEffect(() => {
    if (!isVisible) return
    if (visibleCount >= activityItems.length) return
    const timer = setTimeout(() => {
      setVisibleCount(prev => prev + 1)
    }, 600)
    return () => clearTimeout(timer)
  }, [isVisible, visibleCount])

  return (
    <div ref={ref} className="w-full max-w-4xl mx-auto rounded-2xl border border-border bg-bg-surface overflow-hidden glow-border">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-bg-elevated">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-sm font-medium text-text-primary">AI Agents — Live Activity</span>
        </div>
        <span className="text-xs text-text-tertiary tabular-nums">5 agents active</span>
      </div>

      {/* Activity items */}
      <div className="p-4 space-y-2 min-h-[320px]">
        {activityItems.map((item, idx) => {
          const isVisibleItem = idx < visibleCount
          return (
            <div
              key={idx}
              className={cn(
                'flex items-center gap-3 rounded-lg border border-border bg-bg-elevated p-3 transition-all duration-500',
                isVisibleItem ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8',
              )}
            >
              <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0', 'bg-brand/10')}>
                <item.icon className={cn('h-4 w-4', item.color)} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-text-primary">{item.name}</span>
                  {isVisibleItem ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <div className="h-3 w-3 rounded-full border-2 border-brand/30 border-t-brand animate-spin flex-shrink-0" />
                  )}
                </div>
                <p className="text-xs text-text-tertiary mt-0.5">{isVisibleItem ? item.result : item.action}</p>
              </div>
              <span className={cn('text-xs font-mono', isVisibleItem ? 'text-emerald-400' : 'text-text-tertiary')}>
                {isVisibleItem ? '✓ done' : '...running'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

/* ==================== PANEL 2: Deploy Terminal ==================== */

const deployLines = [
  { text: '$ evolvixos deploy --production', type: 'command' },
  { text: '→ Building application...', type: 'progress' },
  { text: '→ Running 2000+ tests...', type: 'progress' },
  { text: '✓ 133 tests passed', type: 'success' },
  { text: '→ Security scan: 0 critical issues', type: 'progress' },
  { text: '→ Building Docker image...', type: 'progress' },
  { text: '→ Deploying to production...', type: 'progress' },
  { text: '✓ Deployed successfully in 42s', type: 'success' },
  { text: '✓ All 14 services healthy', type: 'success' },
]

function DeployTerminal() {
  const { ref, isVisible } = useScrollReveal<HTMLDivElement>({ threshold: 0.3 })
  const [visibleLines, setVisibleLines] = useState(0)
  const [currentChar, setCurrentChar] = useState(0)

  useEffect(() => {
    if (!isVisible) return
    if (visibleLines >= deployLines.length) {
      const reset = setTimeout(() => {
        setVisibleLines(0)
        setCurrentChar(0)
      }, 4000)
      return () => clearTimeout(reset)
    }

    const line = deployLines[visibleLines]
    if (currentChar < line.text.length) {
      const timer = setTimeout(() => setCurrentChar(prev => prev + 1), 30 + Math.random() * 20)
      return () => clearTimeout(timer)
    } else {
      const timer = setTimeout(() => {
        setVisibleLines(prev => prev + 1)
        setCurrentChar(0)
      }, 350)
      return () => clearTimeout(timer)
    }
  }, [isVisible, visibleLines, currentChar])

  const getColor = (type: string) => {
    switch (type) {
      case 'command': return 'text-text-primary'
      case 'success': return 'text-emerald-400'
      case 'progress': return 'text-text-tertiary'
      default: return 'text-text-secondary'
    }
  }

  return (
    <div ref={ref} className="w-full max-w-4xl mx-auto rounded-2xl border border-border bg-[#0d0d0f] shadow-2xl overflow-hidden glow-border">
      {/* macOS-style title bar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-[#151518]">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-red-500/80" />
          <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
          <div className="h-3 w-3 rounded-full bg-green-500/80" />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Rocket className="h-3.5 w-3.5 text-text-tertiary" />
          <span className="text-xs text-text-tertiary font-mono">evolvixos — deploy</span>
        </div>
      </div>
      {/* Terminal content */}
      <div className="p-5 font-mono text-sm space-y-1.5 min-h-[300px] max-h-[300px] overflow-hidden">
        {deployLines.slice(0, visibleLines).map((line, idx) => (
          <div key={idx} className={getColor(line.type)}>
            <span>{line.text}</span>
          </div>
        ))}
        {visibleLines < deployLines.length && (
          <div className={getColor(deployLines[visibleLines].type)}>
            <span>{deployLines[visibleLines].text.slice(0, currentChar)}</span>
            <span className="ml-0.5 inline-block w-2 h-4 bg-emerald-400/70 animate-pulse" />
          </div>
        )}
        {visibleLines >= deployLines.length && (
          <div className="mt-4 flex items-center gap-2 text-emerald-400">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-xs">Deployment pipeline complete. All systems operational.</span>
          </div>
        )}
      </div>
    </div>
  )
}

/* ==================== PANEL 3: Monitoring Dashboard ==================== */

const monitoringStats = [
  { label: 'CPU Usage', value: 42, unit: '%', color: 'bg-blue-500' },
  { label: 'Memory', value: 63, unit: '%', color: 'bg-amber-500' },
  { label: 'Disk', value: 28, unit: '%', color: 'bg-emerald-500' },
  { label: 'Network I/O', value: 15, unit: '%', color: 'bg-purple-500' },
]

function MonitoringDashboard() {
  const { ref, isVisible } = useScrollReveal<HTMLDivElement>({ threshold: 0.2 })
  const [barWidths, setBarWidths] = useState<number[]>([0, 0, 0, 0])

  useEffect(() => {
    if (!isVisible) return
    const timers = monitoringStats.map((stat, idx) =>
      setTimeout(() => {
        setBarWidths(prev => {
          const next = [...prev]
          next[idx] = stat.value
          return next
        })
      }, idx * 200)
    )
    return () => timers.forEach(clearTimeout)
  }, [isVisible])

  return (
    <div ref={ref} className="w-full max-w-4xl mx-auto rounded-2xl border border-border bg-bg-surface overflow-hidden glow-border">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-bg-elevated">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-brand" />
          <span className="text-sm font-medium text-text-primary">System Monitoring — Live</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-emerald-400 font-medium">All systems operational</span>
        </div>
      </div>

      <div className="p-5">
        {/* Stat cards with animated bars */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {monitoringStats.map((stat, idx) => (
            <div key={idx} className="rounded-xl border border-border bg-bg-elevated p-4">
              <p className="text-xs text-text-tertiary mb-1">{stat.label}</p>
              <p className="text-2xl font-semibold text-text-primary tabular-nums">
                {isVisible ? stat.value : 0}{stat.unit}
              </p>
              {/* Progress bar */}
              <div className="mt-3 h-1.5 rounded-full bg-bg-hover overflow-hidden">
                <div
                  className={cn('h-full rounded-full transition-all duration-1000 ease-out', stat.color)}
                  style={{ width: `${barWidths[idx]}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Mock chart area */}
        <div className="rounded-xl border border-border bg-bg-elevated p-4 h-48 flex items-end justify-between gap-2">
          {[35, 50, 42, 65, 48, 72, 55, 80, 62, 45, 58, 70, 38, 52, 68, 44, 60, 75, 50, 63].map((height, idx) => (
            <div
              key={idx}
              className="flex-1 rounded-t bg-gradient-to-t from-brand/30 to-brand/60 transition-all duration-700 ease-out"
              style={{
                height: isVisible ? `${height}%` : '0%',
                transitionDelay: `${idx * 30}ms`,
              }}
            />
          ))}
        </div>

        {/* Footer stats */}
        <div className="mt-4 flex items-center justify-between text-xs text-text-tertiary">
          <span>Uptime: <span className="text-emerald-400 font-medium">99.98%</span></span>
          <span>Avg Response: <span className="text-text-primary font-medium">42ms</span></span>
          <span>Requests/min: <span className="text-text-primary font-medium">1,247</span></span>
        </div>
      </div>
    </div>
  )
}

/* ==================== MAIN SECTION ==================== */

export function LandingProductDemo() {
  return (
    <div className="mx-auto max-w-5xl px-6 lg:px-8 mt-32" id="product-demo">
      {/* Section title */}
      <Reveal direction="up" className="text-center mb-16">
        <h2 className="text-4xl font-bold tracking-tight text-text-primary">
          See EvolvixOS in action
        </h2>
        <p className="mt-3 text-lg text-text-secondary max-w-2xl mx-auto">
          Watch how autonomous AI agents build, deploy, and monitor your systems —
          all from a single unified platform.
        </p>
      </Reveal>

      {/* Panel 1: AI Agents */}
      <Reveal direction="up" duration={700} className="mb-20">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/5 px-3 py-1 mb-3">
            <Bot className="h-3.5 w-3.5 text-brand" />
            <span className="text-xs font-medium text-brand">Panel 01</span>
          </div>
          <h3 className="text-2xl font-bold text-text-primary">AI agents working in real-time</h3>
          <p className="mt-1 text-sm text-text-tertiary">5 autonomous agents analyzing, reviewing, and improving your codebase 24/7.</p>
        </div>
        <ActivityFeed />
      </Reveal>

      {/* Panel 2: Deploy */}
      <Reveal direction="up" duration={700} className="mb-20">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/5 px-3 py-1 mb-3">
            <Terminal className="h-3.5 w-3.5 text-brand" />
            <span className="text-xs font-medium text-brand">Panel 02</span>
          </div>
          <h3 className="text-2xl font-bold text-text-primary">Deploy with one command</h3>
          <p className="mt-1 text-sm text-text-tertiary">Automated builds, tests, security scans, and deployment — all in one pipeline.</p>
        </div>
        <DeployTerminal />
      </Reveal>

      {/* Panel 3: Monitoring */}
      <Reveal direction="up" duration={700} className="mb-12">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/5 px-3 py-1 mb-3">
            <Activity className="h-3.5 w-3.5 text-brand" />
            <span className="text-xs font-medium text-brand">Panel 03</span>
          </div>
          <h3 className="text-2xl font-bold text-text-primary">Monitor everything in real-time</h3>
          <p className="mt-1 text-sm text-text-tertiary">Live dashboards for CPU, memory, disk, network, and all 14 services.</p>
        </div>
        <MonitoringDashboard />
      </Reveal>
    </div>
  )
}
