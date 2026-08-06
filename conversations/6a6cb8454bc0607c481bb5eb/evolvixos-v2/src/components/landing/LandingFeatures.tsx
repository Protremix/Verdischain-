import { cn } from '@/lib/cn'
import { Reveal } from './Reveal'

interface GridFeature {
  name: string
  description: string
  emoji: string
  size: 'small' | 'medium' | 'large'
}

const features: GridFeature[] = [
  { name: 'AI CTO', description: 'Autonomous architecture decisions, code review, and strategic guidance powered by GPT-4o.', emoji: '🧠', size: 'large' },
  { name: 'Full-Stack Auth', description: 'JWT, OAuth, 2FA, password reset, and account lockout — built in.', emoji: '🔐', size: 'small' },
  { name: 'Real-Time Monitoring', description: 'Prometheus, Grafana, and Loki integration with live dashboards and alerting.', emoji: '📊', size: 'medium' },
  { name: 'Intelligent Automation', description: 'AI-powered workflows that automatically handle code review, testing, deployment, and monitoring without manual intervention.', emoji: '⚡', size: 'large' },
  { name: 'Security First', description: 'Rate limiting, CORS hardening, CSP headers, automated security scanning.', emoji: '🛡️', size: 'medium' },
  { name: 'AI Workspace', description: '5 specialized AI agents for architecture, planning, review, and code generation.', emoji: '🤖', size: 'medium' },
  { name: 'Deployment Automation', description: 'One-command deploy with Docker, systemd, and CI/CD pipelines.', emoji: '🚀', size: 'small' },
  { name: 'Knowledge Base', description: 'Architecture decisions, API docs, runbooks, and FAQs.', emoji: '📚', size: 'small' },
  { name: 'Auto Backup', description: 'Restic-based encrypted backups with 7-day retention and one-click restore.', emoji: '💾', size: 'medium' },
]

const sizeClasses: Record<GridFeature['size'], string> = {
  small: 'col-span-1',
  medium: 'col-span-2 md:col-span-2 lg:col-span-2',
  large: 'col-span-2 md:col-span-2 lg:col-span-2 row-span-2',
}

export function LandingFeatures() {
  return (
    <div className="mx-auto my-16 flex max-w-7xl flex-col gap-4 px-6 lg:px-8" id="features">
      <Reveal direction="up" className="text-center mb-8">
        <h2 className="text-3xl font-bold tracking-tight text-text-primary">Everything you need to ship</h2>
        <p className="mt-2 text-text-secondary">A complete AI-powered engineering platform, from idea to production.</p>
      </Reveal>

      <div className="grid auto-rows-[minmax(140px,auto)] grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
        {features.map((feature, idx) => (
          <Reveal
            key={feature.name}
            direction="scale"
            delay={idx * 80}
            duration={500}
            className={cn(
              'group rounded-xl border border-border bg-bg-surface p-5 transition-all duration-300 hover:border-brand/30 hover:shadow-lg cursor-pointer card-lift glow-border',
              sizeClasses[feature.size],
            )}
          >
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-3 text-4xl transition-transform duration-300 group-hover:scale-125">{feature.emoji}</div>
              <h3 className="text-sm font-semibold text-text-primary mb-2">{feature.name}</h3>
              <p className="text-xs text-text-tertiary leading-relaxed">{feature.description}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  )
}
