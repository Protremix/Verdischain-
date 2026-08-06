import { Link } from 'react-router-dom'
import { Cpu, Bot, Shield, GitBranch, Zap, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Reveal } from './Reveal'

export function LandingAIReady() {
  return (
    <div className="mx-auto max-w-7xl px-6 lg:px-8 mt-24" id="ai-agents">
      <Reveal direction="scale" duration={700}>
        <div className="rounded-2xl border border-border bg-gradient-to-br from-bg-surface to-bg-elevated overflow-hidden glow-border">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
            {/* Left: Content */}
            <div className="p-8 lg:p-12">
              <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/5 px-3 py-1 mb-6 animate-badge-pop">
                <Bot className="h-3.5 w-3.5 text-brand" />
                <span className="text-xs font-medium text-brand">AI-Ready</span>
              </div>
              <h2 className="text-3xl font-bold tracking-tight text-text-primary">
                Meet your 24/7
                <span className="block text-text-tertiary text-2xl mt-1">AI engineering team</span>
              </h2>
              <p className="mt-4 text-text-secondary leading-relaxed">
                Five specialized AI agents that don't just suggest — they execute. Each one
                analyzes your codebase, makes engineering decisions with full project context,
                and implements changes automatically. Powered by GPT-4o.
              </p>

              <div className="mt-8 space-y-4">
                {[
                  { icon: Cpu, name: 'AI CTO', desc: 'Architecture decisions and strategic guidance' },
                  { icon: Bot, name: 'AI Architect', desc: 'Code review and system design' },
                  { icon: GitBranch, name: 'AI Planner', desc: 'Roadmaps and sprint planning' },
                  { icon: Shield, name: 'AI Reviewer', desc: 'Security and quality audits' },
                  { icon: Zap, name: 'AI Developer', desc: 'Code generation and refactoring' },
                ].map((agent, idx) => (
                  <Reveal key={agent.name} direction="left" delay={idx * 100} duration={500}>
                    <div className="flex items-center gap-3 group">
                      <div className="h-9 w-9 rounded-lg bg-brand/10 flex items-center justify-center flex-shrink-0 transition-all duration-300 group-hover:bg-brand/20 group-hover:scale-110">
                        <agent.icon className="h-4 w-4 text-brand" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-text-primary">{agent.name}</p>
                        <p className="text-xs text-text-tertiary">{agent.desc}</p>
                      </div>
                    </div>
                  </Reveal>
                ))}
              </div>

              <Link to="/" className="inline-block mt-8">
                <Button variant="outline" size="sm" icon={<ArrowRight className="h-3.5 w-3.5" />} className="card-lift">
                  Explore AI Workspace
                </Button>
              </Link>
            </div>

            {/* Right: Visual */}
            <div className="bg-bg-elevated p-8 lg:p-12 flex items-center justify-center border-l border-border">
              <div className="w-full max-w-sm space-y-3">
                {/* Mock chat */}
                <Reveal direction="right" delay={200} duration={600}>
                  <div className="rounded-lg bg-bg-surface border border-border p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-6 w-6 rounded bg-brand-gradient flex items-center justify-center">
                        <Cpu className="h-3 w-3 text-white" />
                      </div>
                      <span className="text-xs font-medium text-text-primary">AI CTO</span>
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse ml-auto" />
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      Analyzed microservices architecture. Security score: 8.5/10. Recommending
                      API gateway pattern for better request routing.
                    </p>
                  </div>
                </Reveal>

                <Reveal direction="right" delay={400} duration={600}>
                  <div className="rounded-lg bg-bg-surface border border-border p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-6 w-6 rounded bg-brand-gradient flex items-center justify-center">
                        <Shield className="h-3 w-3 text-white" />
                      </div>
                      <span className="text-xs font-medium text-text-primary">AI Reviewer</span>
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse ml-auto" />
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      Security audit complete. 0 critical, 2 medium findings.
                      Recommending CSP header enforcement on all API routes.
                    </p>
                  </div>
                </Reveal>

                <Reveal direction="right" delay={600} duration={600}>
                  <div className="rounded-lg bg-bg-surface border border-border p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-6 w-6 rounded bg-brand-gradient flex items-center justify-center">
                        <GitBranch className="h-3 w-3 text-white" />
                      </div>
                      <span className="text-xs font-medium text-text-primary">AI Planner</span>
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse ml-auto" />
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      Q3 roadmap generated. 12 epics, 47 stories. Priority:
                      API refactoring, test coverage expansion, CI/CD pipeline upgrades.
                    </p>
                  </div>
                </Reveal>
              </div>
            </div>
          </div>
        </div>
      </Reveal>
    </div>
  )
}
