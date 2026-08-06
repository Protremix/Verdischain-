import { cn } from '@/lib/cn'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, Cpu, Shield, Bot, GitBranch } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { useAnimatedCounter } from '@/hooks/useAnimatedCounter'

function AnimatedStat({ value, label, suffix = '', delay = 0 }: { value: number; label: string; suffix?: string; delay?: number }) {
  const { ref, isVisible } = useScrollReveal<HTMLDivElement>({ threshold: 0.3 })
  const count = useAnimatedCounter(value, 2000, isVisible)

  return (
    <div
      ref={ref}
      style={{ transitionDelay: `${delay}ms`, transition: 'opacity 0.6s ease, transform 0.6s ease' }}
      className={cn(isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4')}
    >
      <p className="text-3xl font-semibold text-text-primary tabular-nums">
        {count}{suffix}
      </p>
      <p className="text-sm text-text-tertiary mt-1">{label}</p>
    </div>
  )
}

export function LandingHero() {
  return (
    <div className="relative w-full pt-32 pb-16 overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute right-0 top-0 -z-10 w-full blur-3xl overflow-hidden" aria-hidden="true">
        <div
          className="aspect-[1020/880] w-[60rem] bg-gradient-to-tr from-indigo-500/20 via-purple-500/10 to-blue-500/20 flex-none animate-gradient"
          style={{ clipPath: 'polygon(80% 20%, 90% 55%, 50% 100%, 70% 30%, 20% 50%, 50% 0%)' }}
        />
      </div>
      <div className="absolute inset-x-0 top-[60%] -z-10 blur-3xl overflow-hidden" aria-hidden="true">
        <div
          className="aspect-[1020/880] w-[80rem] bg-gradient-to-br from-indigo-500/15 to-purple-500/10 relative -left-1/4 animate-glow"
          style={{ clipPath: 'ellipse(80% 30% at 80% 50%)' }}
        />
      </div>

      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          {/* Badge with pop animation */}
          <div
            className="inline-flex items-center gap-2 rounded-full border border-border bg-bg-surface/50 backdrop-blur-sm px-4 py-1.5 mb-8 animate-badge-pop"
          >
            <Sparkles className="h-3.5 w-3.5 text-brand" />
            <span className="text-xs font-medium text-text-secondary">The AI Engineering Operating System</span>
          </div>

          {/* Headline with shimmer gradient */}
          <h1 className="text-5xl font-bold tracking-tight text-text-primary sm:text-6xl animate-slide-up">
            Build software with
            <span className="block sm:inline bg-gradient-to-r from-indigo-400 via-purple-400 to-blue-400 via-pink-400 bg-clip-text text-transparent animate-shimmer">
              {' '}autonomous intelligence
            </span>
          </h1>

          {/* Subheadline */}
          <p
            className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-text-secondary animate-fade-in"
            style={{ animationDelay: '0.2s', opacity: 0, animationFillMode: 'forwards' }}
          >
            EvolvixOS is the AI engineering platform that helps you design, build, deploy, and secure
            world-class software systems — with autonomous AI agents that never stop improving.
          </p>

          {/* CTA buttons with stagger */}
          <div
            className="mt-10 flex items-center justify-center gap-x-6 animate-slide-up"
            style={{ animationDelay: '0.4s', opacity: 0, animationFillMode: 'forwards' }}
          >
            <Link to="/">
              <Button size="lg" variant="outline" className="card-lift">Learn More</Button>
            </Link>
            <Link to="/">
              <Button size="lg" icon={<ArrowRight className="h-4 w-4" />} className="card-lift">
                Get Started
              </Button>
            </Link>
          </div>

          {/* Stats bar with animated counters */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <AnimatedStat value={5} label="AI Agents" delay={0} />
            <AnimatedStat value={100} label="Token Supply" suffix="B" delay={100} />
            <AnimatedStat value={14} label="Services Online" delay={200} />
          </div>
        </div>

        {/* Product preview card with float animation */}
        <div className="mt-16 flow-root">
          <div className="hidden justify-center rounded-xl md:flex lg:rounded-2xl lg:p-4 animate-float" style={{ animationDelay: '0.5s' }}>
            <div className="max-w-4xl w-full rounded-xl border border-border bg-bg-surface shadow-2xl overflow-hidden glow-border">
              {/* Mock app screenshot */}
              <div className="flex">
                {/* Sidebar */}
                <div className="w-48 bg-bg-elevated border-r border-border p-3 space-y-1">
                  <div className="flex items-center gap-2 px-2 py-1.5 mb-2">
                    <img src="/evolvixos-icon.png" alt="EvolvixOS" className="h-6 w-6 object-contain" />
                    <span className="text-xs font-semibold text-text-primary">EvolvixOS</span>
                  </div>
                  {['Dashboard', 'Projects', 'AI Workspace', 'Monitoring', 'Security'].map((item, i) => (
                    <div key={item} className={cn('flex items-center gap-2 px-2 py-1.5 rounded text-xs', i === 0 ? 'bg-brand/10 text-brand' : 'text-text-tertiary')}>
                      {i === 0 && <div className="h-1.5 w-1.5 rounded-full bg-brand animate-pulse" />}
                      {item}
                    </div>
                  ))}
                </div>
                {/* Main area */}
                <div className="flex-1 p-6">
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {[1, 2, 3].map(i => (
                      <div key={i} className="rounded-lg border border-border bg-bg-surface p-3">
                        <div className="h-2 w-12 bg-bg-hover rounded mb-2" />
                        <div className="h-5 w-16 bg-brand/20 rounded" />
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg border border-border bg-bg-surface p-4 h-32 flex items-center justify-center">
                      <Cpu className="h-8 w-8 text-text-tertiary" />
                    </div>
                    <div className="rounded-lg border border-border bg-bg-surface p-4 h-32 flex items-center justify-center">
                      <Bot className="h-8 w-8 text-text-tertiary" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll-down indicator */}
        <div className="flex justify-center mt-12">
          <div className="flex flex-col items-center gap-1">
            <span className="text-xs text-text-tertiary">Scroll to explore</span>
            <div className="h-8 w-5 rounded-full border-2 border-border flex items-start justify-center p-1">
              <div className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-scroll-down" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
