interface Testimonial {
  name: string
  role: string
  initials: string
  quote: string
}

const testimonials: Testimonial[] = [
  { name: 'Rojs Gordons', role: 'Founder & CEO, Protremix', initials: 'RG', quote: 'EvolvixOS transformed how we build software. The AI agents handle architecture decisions and code reviews autonomously, letting our team focus on shipping.' },
  { name: 'Engineering Team', role: 'Verdis Chain Core', initials: 'VC', quote: 'The integration with our Substrate blockchain is seamless. Real-time monitoring, automated security audits, and one-command deployment saved us weeks.' },
  { name: 'Security Lead', role: 'AegisOS', initials: 'AL', quote: 'The security scanner catches issues before they reach production. Rate limiting, CORS hardening, and CSP headers are all built in — no manual setup needed.' },
  { name: 'DevOps', role: 'EvolvixOS Infrastructure', initials: 'DI', quote: '14 Docker containers, automated backups, Grafana dashboards, and Loki log aggregation — all deployed and monitored from a single platform.' },
  { name: 'Product Team', role: 'Anerium Fintech', initials: 'PT', quote: 'The AI CTO agent gives us architecture recommendations with engineering reasoning. It\'s like having a Principal Engineer available 24/7.' },
  { name: 'QA Lead', role: 'Verdis Wallet', initials: 'QA', quote: 'Automated testing pipelines with 2000+ tests, security audits, and quality gates. We ship with confidence.' },
]

export function LandingTestimonials() {
  return (
    <div className="mx-auto mt-32 max-w-7xl px-6 lg:px-8" id="testimonials">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold tracking-tight text-text-primary">What our team says</h2>
        <p className="mt-2 text-text-secondary">Real feedback from engineers using EvolvixOS every day.</p>
      </div>

      <div className="columns-1 gap-4 px-0 md:columns-2 md:gap-6 lg:columns-3">
        {testimonials.map((t, idx) => (
          <div key={idx} className="mb-4 break-inside-avoid">
            <div className="rounded-xl border border-border bg-bg-surface p-5 flex flex-col">
              <blockquote className="mb-4">
                <p className="text-sm italic text-text-secondary leading-relaxed">"{t.quote}"</p>
              </blockquote>
              <div className="flex items-center gap-3 mt-auto pt-2">
                <div className="h-10 w-10 rounded-full bg-brand/10 text-brand flex items-center justify-center text-xs font-medium flex-shrink-0">
                  {t.initials}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-text-primary truncate">{t.name}</p>
                  <p className="text-xs text-text-tertiary truncate">{t.role}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
