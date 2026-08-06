import { Reveal } from './Reveal'

const trustedBrands = [
  'Protremix', 'Anerium', 'AegisOS', 'EvolvixOS',
  'GitHub', 'Docker', 'GPT-4o', 'Grafana',
  'Prometheus', 'Redis', 'PostgreSQL', 'Nginx',
]

export function LandingTrustedBy() {
  return (
    <div className="mx-auto max-w-7xl px-6 lg:px-8 mt-12 mb-8">
      <Reveal direction="fade" duration={600}>
        <p className="text-center text-xs font-medium uppercase tracking-widest text-text-tertiary mb-6">
          Powered by world-class infrastructure
        </p>
        <div className="relative overflow-hidden">
          {/* Fade edges */}
          <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-bg-base to-transparent z-10 pointer-events-none" />
          <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-bg-base to-transparent z-10 pointer-events-none" />

          {/* Marquee */}
          <div className="flex gap-12 animate-marquee whitespace-nowrap">
            {[...trustedBrands, ...trustedBrands].map((brand, idx) => (
              <span
                key={idx}
                className="text-lg font-bold text-text-tertiary/60 hover:text-text-secondary transition-colors duration-300 cursor-default"
              >
                {brand}
              </span>
            ))}
          </div>
        </div>
      </Reveal>
    </div>
  )
}
