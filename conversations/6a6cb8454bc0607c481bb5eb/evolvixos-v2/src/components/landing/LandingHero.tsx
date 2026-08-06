import { cn } from '@/lib/cn'
import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { useAnimatedCounter } from '@/hooks/useAnimatedCounter'
import { useState, useEffect, useRef } from 'react'

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

const terminalLines = [
  { text: '$ evolvixos deploy --production', color: 'text-text-primary' },
  { text: '→ Building application...', color: 'text-text-tertiary' },
  { text: '→ Running 2000+ tests...', color: 'text-text-tertiary' },
  { text: '✓ 133 tests passed', color: 'text-emerald-400' },
  { text: '→ Security scan: 0 critical issues', color: 'text-text-tertiary' },
  { text: '✓ Deployed to production in 42s', color: 'text-emerald-400' },
  { text: '$ evolvixos agent run --cto', color: 'text-text-primary' },
  { text: '→ AI CTO analyzing architecture...', color: 'text-text-tertiary' },
  { text: '→ Security score: 8.5/10', color: 'text-blue-400' },
  { text: '→ Recommendation: Apply CSP headers', color: 'text-amber-400' },
  { text: '✓ Architecture review complete', color: 'text-emerald-400' },
  { text: '$ evolvixos monitor --live', color: 'text-text-primary' },
  { text: '→ 14 services online', color: 'text-text-tertiary' },
  { text: '✓ All systems operational', color: 'text-emerald-400' },
]

function AnimatedTerminal() {
  const [visibleLines, setVisibleLines] = useState<number>(0)
  const [currentChar, setCurrentChar] = useState<number>(0)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (visibleLines >= terminalLines.length) {
      const resetTimer = setTimeout(() => {
        setVisibleLines(0)
        setCurrentChar(0)
      }, 3000)
      return () => clearTimeout(resetTimer)
    }

    const currentLine = terminalLines[visibleLines]
    if (currentChar < currentLine.text.length) {
      const charTimer = setTimeout(() => {
        setCurrentChar(prev => prev + 1)
      }, 25 + Math.random() * 30)
      return () => clearTimeout(charTimer)
    } else {
      const lineTimer = setTimeout(() => {
        setVisibleLines(prev => prev + 1)
        setCurrentChar(0)
      }, 400)
      return () => clearTimeout(lineTimer)
    }
  }, [visibleLines, currentChar])

  return (
    <div className="w-full max-w-3xl mx-auto rounded-xl border border-border bg-[#0d0d0f] shadow-2xl overflow-hidden glow-border animate-float" style={{ animationDelay: '0.5s' }}>
      {/* Title bar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-[#151518]">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-red-500/80" />
          <div className="h-3 w-3 rounded-full bg-yellow-500/80" />
          <div className="h-3 w-3 rounded-full bg-green-500/80" />
        </div>
        <span className="ml-2 text-xs text-text-tertiary font-mono">evolvixos — terminal</span>
      </div>
      {/* Terminal content */}
      <div ref={containerRef} className="p-5 font-mono text-sm space-y-1 min-h-[280px] max-h-[280px] overflow-hidden">
        {terminalLines.slice(0, visibleLines).map((line, idx) => (
          <div key={idx} className={line.color}>
            <span className="select-none">{line.text}</span>
            <span className="ml-1 inline-block w-2 h-4 bg-text-primary/50 animate-pulse" />
          </div>
        ))}
        {visibleLines < terminalLines.length && (
          <div className={terminalLines[visibleLines].color}>
            <span className="select-none">{terminalLines[visibleLines].text.slice(0, currentChar)}</span>
            <span className="ml-0.5 inline-block w-2 h-4 bg-emerald-400/70 animate-pulse" />
          </div>
        )}
      </div>
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
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-bg-surface/50 backdrop-blur-sm px-4 py-1.5 mb-8 animate-badge-pop">
            <Sparkles className="h-3.5 w-3.5 text-brand" />
            <span className="text-xs font-medium text-text-secondary">The AI Engineering Operating System</span>
          </div>

          {/* Headline with shimmer gradient */}
          <h1 className="text-5xl font-bold tracking-tight text-text-primary sm:text-6xl animate-slide-up">
            Ship software faster with
            <span className="block sm:inline bg-gradient-to-r from-indigo-400 via-purple-400 to-blue-400 bg-clip-text text-transparent animate-shimmer">
              {' '}autonomous AI engineers
            </span>
          </h1>

          {/* Subheadline */}
          <p
            className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-text-secondary animate-fade-in"
            style={{ animationDelay: '0.2s', opacity: 0, animationFillMode: 'forwards' }}
          >
            EvolvixOS is the world's first AI Engineering Operating System. Five autonomous AI agents
            design, build, deploy, and secure your software — 24/7. No scripts. No manual ops.
            Just autonomous engineering.
          </p>

          {/* CTA buttons with stagger — more action-oriented */}
          <div
            className="mt-10 flex items-center justify-center gap-x-6 animate-slide-up"
            style={{ animationDelay: '0.4s', opacity: 0, animationFillMode: 'forwards' }}
          >
            <Link to="/">
              <Button size="lg" variant="outline" className="card-lift">See How It Works</Button>
            </Link>
            <Link to="/">
              <Button size="lg" icon={<ArrowRight className="h-4 w-4" />} className="card-lift">
                Start Building Free
              </Button>
            </Link>
          </div>

          {/* Stats bar with animated counters */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <AnimatedStat value={5} label="AI Agents" delay={0} />
            <AnimatedStat value={2000} label="Tests Automated" suffix="+" delay={100} />
            <AnimatedStat value={14} label="Services Online" delay={200} />
          </div>
        </div>

        {/* Animated terminal — video-like typing demo */}
        <div className="mt-16 flow-root">
          <AnimatedTerminal />
        </div>

        {/* Scroll-down indicator */}
        <div className="flex justify-center mt-12">
          <div className="flex flex-col items-center gap-1">
            <span className="text-xs text-text-tertiary">Scroll to explore</span>
            <div className="h-8 w-5 rounded-full border-2 border-border flex items-start justify-center p-1">
              <div className="h-2 w-1 rounded-full bg-brand animate-bounce" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
