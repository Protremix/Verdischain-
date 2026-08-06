import { Reveal } from './Reveal'
import { Cpu, Bot, Shield, GitBranch, Zap, Clock, ArrowRight, CheckCircle2 } from 'lucide-react'

const differentiators = [
  {
    icon: Clock,
    title: '24/7 Autonomous Operation',
    description: 'Unlike traditional DevOps tools that wait for you to act, EvolvixOS agents continuously monitor, analyze, and improve your systems — even while you sleep.',
    metric: 'Never stops working',
  },
  {
    icon: Bot,
    title: 'AI Agents That Actually Execute',
    description: 'Other platforms suggest. EvolvixOS agents act. They don\'t just recommend changes — they implement, test, and deploy them automatically with full project context.',
    metric: 'Suggestion → Implementation',
  },
  {
    icon: Shield,
    title: 'Security Built Into Every Layer',
    description: 'Rate limiting, CORS hardening, CSP headers, automated security scanning, and encrypted backups — all configured by default, not as afterthoughts.',
    metric: 'Zero-config security',
  },
  {
    icon: Zap,
    title: 'One Command, Full Pipeline',
    description: 'Build, test, scan, deploy, and monitor with a single command. No scripts to write, no pipelines to configure, no YAML to debug.',
    metric: '42s to production',
  },
]

const comparedTo = [
  { feature: 'Autonomous AI agents', evolvixos: true, traditional: false },
  { feature: 'GPT-4o powered decisions', evolvixos: true, traditional: false },
  { feature: 'Auto-deploy pipeline', evolvixos: true, traditional: 'Manual' },
  { feature: '24/7 monitoring + alerting', evolvixos: true, traditional: 'Add-on' },
  { feature: 'Built-in security scanning', evolvixos: true, traditional: false },
  { feature: 'Self-hosting included', evolvixos: true, traditional: 'Enterprise only' },
  { feature: 'Setup time', evolvixos: '< 1 hour', traditional: 'Days to weeks' },
]

export function LandingWhyEvolvixOS() {
  return (
    <div className="mx-auto max-w-7xl px-6 lg:px-8 mt-32" id="why-evolvixos">
      {/* Section title */}
      <Reveal direction="up" className="text-center mb-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/5 px-3 py-1 mb-4">
          <Cpu className="h-3.5 w-3.5 text-brand" />
          <span className="text-xs font-medium text-brand">Why EvolvixOS</span>
        </div>
        <h2 className="text-4xl font-bold tracking-tight text-text-primary">
          Not another DevOps tool.
          <span className="block text-text-tertiary text-2xl mt-2">An AI Engineering Operating System.</span>
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-text-secondary">
          Traditional tools wait for you to configure them. EvolvixOS agents take initiative —
          they analyze your systems, identify problems, implement solutions, and deploy fixes
          autonomously. That's the difference between a tool and an operating system.
        </p>
      </Reveal>

      {/* Differentiator cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
        {differentiators.map((item, idx) => (
          <Reveal key={item.title} direction="up" delay={idx * 100} duration={500}>
            <div className="rounded-2xl border border-border bg-bg-surface p-6 card-lift glow-border h-full">
              <div className="flex items-start gap-4">
                <div className="h-11 w-11 rounded-xl bg-brand/10 flex items-center justify-center flex-shrink-0">
                  <item.icon className="h-5 w-5 text-brand" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-text-primary">{item.title}</h3>
                    <span className="text-xs font-medium text-brand bg-brand/10 px-2 py-0.5 rounded-full">{item.metric}</span>
                  </div>
                  <p className="text-sm text-text-tertiary leading-relaxed">{item.description}</p>
                </div>
              </div>
            </div>
          </Reveal>
        ))}
      </div>

      {/* Comparison table */}
      <Reveal direction="scale" duration={700}>
        <div className="rounded-2xl border border-border bg-bg-surface overflow-hidden glow-border">
          <div className="px-6 py-4 border-b border-border bg-bg-elevated">
            <h3 className="text-lg font-semibold text-text-primary">EvolvixOS vs. Traditional DevOps</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-6 py-4 text-sm font-medium text-text-tertiary">Feature</th>
                  <th className="text-center px-6 py-4 text-sm font-semibold text-brand">EvolvixOS</th>
                  <th className="text-center px-6 py-4 text-sm font-medium text-text-tertiary">Traditional Tools</th>
                </tr>
              </thead>
              <tbody>
                {comparedTo.map((row, idx) => (
                  <tr key={row.feature} className={idx % 2 === 0 ? 'bg-bg-elevated/30' : ''}>
                    <td className="px-6 py-3.5 text-sm text-text-secondary">{row.feature}</td>
                    <td className="px-6 py-3.5 text-center">
                      {row.evolvixos === true ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-400 mx-auto" />
                      ) : (
                        <span className="text-sm font-medium text-text-primary">{row.evolvixos}</span>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-center text-sm text-text-tertiary">
                      {row.traditional === false ? (
                        <span className="text-text-tertiary">—</span>
                      ) : (
                        row.traditional
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Reveal>
    </div>
  )
}
