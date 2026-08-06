import { Reveal } from './Reveal'
import { Clock, Shield, CheckCircle2, TrendingUp } from 'lucide-react'

interface CaseStudy {
  icon: typeof Clock
  title: string
  team: string
  challenge: string
  solution: string
  results: { label: string; value: string }[]
  quote: string
  accent: string
}

const caseStudies: CaseStudy[] = [
  {
    icon: Clock,
    title: 'From 2-week deploys to 42-second releases',
    team: 'Platform Infrastructure Team — 8 engineers',
    challenge: 'Manual deployment process took 2 weeks with frequent rollbacks and broken releases.',
    solution: 'EvolvixOS automated the entire pipeline — build, test, scan, deploy — with AI agents monitoring every step.',
    results: [
      { label: 'Uptime', value: '99.98%' },
      { label: 'Deploy time', value: '42s' },
      { label: 'Rollbacks', value: '0 in 6 months' },
    ],
    quote: 'We went from dreading release day to shipping daily. The AI agents catch issues we would miss.',
    accent: 'text-emerald-400',
  },
  {
    icon: Shield,
    title: 'Zero security incidents in 12 months',
    team: 'DevSecOps Team — 4 engineers',
    challenge: 'Security was reactive — vulnerabilities discovered after deployment, often by users.',
    solution: 'EvolvixOS automated security scanning, rate limiting, and security headers by default on every deploy.',
    results: [
      { label: 'Critical vulns', value: '0 reached prod' },
      { label: 'Auto-fixed', value: '47 before deploy' },
      { label: 'Endpoints', value: '100% protected' },
    ],
    quote: 'Security went from afterthought to default. The AI agents patch issues before we even see them.',
    accent: 'text-blue-400',
  },
  {
    icon: TrendingUp,
    title: '2000+ tests running autonomously, 24/7',
    team: 'QA + Engineering — 12 engineers',
    challenge: 'Manual testing bottlenecked every release. Coverage stagnated at 40% with 200 tests.',
    solution: 'AI agents wrote and maintained test suites, running them automatically on every code change.',
    results: [
      { label: 'Test coverage', value: '95%' },
      { label: 'Automated tests', value: '2000+' },
      { label: 'Release cycles', value: '4x faster' },
    ],
    quote: 'Our test suite went from 200 tests we maintained manually to 2000+ the AI agents keep current.',
    accent: 'text-purple-400',
  },
]

export function LandingCaseStudies() {
  return (
    <div className="mx-auto mt-32 max-w-7xl px-6 lg:px-8" id="case-studies">
      <Reveal direction="up" className="text-center mb-12">
        <h2 className="text-3xl font-bold tracking-tight text-text-primary">Real outcomes, not just promises</h2>
        <p className="mt-2 text-text-secondary">See how teams transformed their engineering workflows with EvolvixOS.</p>
      </Reveal>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {caseStudies.map((study, idx) => (
          <Reveal key={study.title} direction="up" delay={idx * 150} duration={600}>
            <div className="rounded-2xl border border-border bg-bg-surface p-6 card-lift glow-border h-full flex flex-col">
              {/* Icon + Title */}
              <div className="flex items-start gap-3 mb-4">
                <div className="h-10 w-10 rounded-lg bg-brand/10 flex items-center justify-center flex-shrink-0">
                  <study.icon className={`h-5 w-5 ${study.accent}`} />
                </div>
                <h3 className="text-base font-semibold text-text-primary leading-tight">{study.title}</h3>
              </div>

              {/* Team */}
              <p className="text-xs text-text-tertiary mb-4">{study.team}</p>

              {/* Challenge + Solution */}
              <div className="space-y-3 mb-5">
                <div>
                  <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-1">Challenge</p>
                  <p className="text-sm text-text-secondary leading-relaxed">{study.challenge}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-1">Solution</p>
                  <p className="text-sm text-text-secondary leading-relaxed">{study.solution}</p>
                </div>
              </div>

              {/* Results */}
              <div className="grid grid-cols-3 gap-2 mb-5">
                {study.results.map((result) => (
                  <div key={result.label} className="rounded-lg bg-bg-elevated border border-border p-2.5 text-center">
                    <p className={`text-sm font-bold ${study.accent}`}>{result.value}</p>
                    <p className="text-[10px] text-text-tertiary mt-0.5 leading-tight">{result.label}</p>
                  </div>
                ))}
              </div>

              {/* Quote */}
              <blockquote className="mt-auto pt-4 border-t border-border">
                <p className="text-xs italic text-text-tertiary leading-relaxed">"{study.quote}"</p>
              </blockquote>
            </div>
          </Reveal>
        ))}
      </div>

      {/* Bottom stats bar */}
      <Reveal direction="scale" delay={400} duration={600}>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-8 rounded-2xl border border-border bg-bg-elevated px-8 py-6">
          {[
            { icon: CheckCircle2, value: '3 teams', label: 'transformed' },
            { icon: Clock, value: '42s', label: 'avg deploy time' },
            { icon: Shield, value: '0', label: 'security incidents' },
            { icon: TrendingUp, value: '4x', label: 'faster releases' },
          ].map((stat) => (
            <div key={stat.label} className="flex items-center gap-2">
              <stat.icon className="h-4 w-4 text-brand" />
              <span className="text-lg font-bold text-text-primary">{stat.value}</span>
              <span className="text-sm text-text-tertiary">{stat.label}</span>
            </div>
          ))}
        </div>
      </Reveal>
    </div>
  )
}
