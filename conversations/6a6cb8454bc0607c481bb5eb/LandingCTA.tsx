import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Reveal } from './Reveal'

export function LandingCTA() {
  return (
    <div className="mx-auto max-w-7xl px-6 lg:px-8 mt-24 mb-16">
      <Reveal direction="scale" duration={700}>
        <div className="relative rounded-3xl overflow-hidden border border-border bg-gradient-to-br from-bg-surface to-bg-elevated p-12 lg:p-20 text-center glow-border">
          {/* Animated gradient orbs */}
          <div className="absolute -top-20 -left-20 w-60 h-60 rounded-full bg-brand/10 blur-3xl animate-glow" aria-hidden="true" />
          <div className="absolute -bottom-20 -right-20 w-60 h-60 rounded-full bg-indigo-500/10 blur-3xl animate-float" aria-hidden="true" />

          <div className="relative z-10">
            <h2 className="text-4xl font-bold tracking-tight text-text-primary">
              Ready to ship with
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-blue-400 bg-clip-text text-transparent animate-shimmer">
                {' '}autonomous AI engineers
              </span>
              ?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-text-secondary">
              Stop configuring tools. Start shipping software. Deploy EvolvixOS in under an hour and let AI agents handle the engineering — while you focus on building.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg" icon={<ArrowRight className="h-4 w-4" />} className="card-lift">
                  Start Building Free
                </Button>
              </Link>
              <Link to="/support">
                <Button size="lg" variant="secondary" className="card-lift">
                  Book a Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </Reveal>
    </div>
  )
}
