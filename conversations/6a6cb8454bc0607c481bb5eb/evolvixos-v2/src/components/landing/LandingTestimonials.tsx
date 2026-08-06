import { Reveal } from './Reveal'

interface Testimonial {
  name: string
  role: string
  initials: string
  quote: string
  metric: string
}

const testimonials: Testimonial[] = [
  { name: 'Rojs Gordons', role: 'Founder & CEO, Protremix', initials: 'RG', quote: 'EvolvixOS transformed how we build software. The AI agents handle architecture decisions and code reviews autonomously, letting our team focus on shipping.', metric: '3x faster delivery' },
  { name: 'Engineering Team', role: 'Platform Infrastructure', initials: 'ET', quote: 'Real-time monitoring, automated security audits, and one-command deployment saved us weeks of manual work. It just works.', metric: '80% less manual ops' },
  { name: 'Security Lead', role: 'DevSecOps', initials: 'SL', quote: 'The security scanner catches issues before they reach production. Rate limiting, CORS hardening, and CSP headers are all built in — no manual setup needed.', metric: '0 security incidents' },
  { name: 'DevOps Engineer', role: 'Infrastructure', initials: 'DI', quote: '14 Docker containers, automated backups, Grafana dashboards, and Loki log aggregation — all deployed and monitored from a single platform.', metric: '1 command to deploy' },
  { name: 'Product Team', role: 'Engineering', initials: 'PT', quote: 'The AI CTO agent gives us architecture recommendations with engineering reasoning. It is like having a Principal Engineer available 24/7.', metric: '24/7 AI coverage' },
  { name: 'QA Lead', role: 'Quality Assurance', initials: 'QA', quote: 'Automated testing pipelines with 2000+ tests, security audits, and quality gates. We ship with confidence.', metric: '2000+ automated tests' },
]

export function LandingTestimonials() {
  return (
    <div className="mx-auto mt-32 max-w-7xl px-6 lg:px-8" id="testimonials">
      <Reveal direction="up" className="text-center mb-12">
        <h2 className="text-3xl font-bold tracking-tight text-text-primary">Real results from real engineers</h2>
        <p className="mt-2 text-text-secondary">Teams using EvolvixOS ship faster, safer, and smarter.</p>
      </Reveal>

      <div className="columns-1 gap-4 px-0 md:columns-2 md:gap-6 lg:columns-3">
        {testimonials.map((t, idx) => (
          <Reveal
            key={idx}
            direction="up"
            delay={(idx % 3) * 120}
            duration={500}
            className="mb-4 break-inside-avoid"
          >
            <div className="rounded-xl border border-border bg-bg-surface p-5 flex flex-col card-lift glow-border">
              {/* Metric badge */}
              <div className="mb-3 inline-flex items-center gap-1.5 self-start rounded-full bg-brand/10 px-2.5 py-1">
                <span className="text-xs font-semibold text-brand">{t.metric}</span>
              </div>
              <blockquote className="mb-4">
                <p className="text-sm italic text-text-secondary leading-relaxed">"{t.quote}"</p>
              </blockquote>
              <div className="flex items-center gap-3 mt-auto pt-2">
                <div className="h-10 w-10 rounded-full bg-brand/10 text-brand flex items-center justify-center text-xs font-medium flex-shrink-0 transition-transform duration-300 hover:scale-110">
                  {t.initials}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-text-primary truncate">{t.name}</p>
                  <p className="text-xs text-text-tertiary truncate">{t.role}</p>
                </div>
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </div>
  )
}
