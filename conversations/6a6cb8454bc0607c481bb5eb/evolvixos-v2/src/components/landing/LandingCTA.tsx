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
              Ready to build with
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-blue-400 bg-clip-text text-transparent animate-shimmer">
                {' '}autonomous intelligence
              </span>
              ?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-text-secondary">
              Join the next generation of AI-powered engineering. Start building world-class
              software systems with autonomous AI agents today.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link to="/">
                <Button size="lg" icon={<ArrowRight className="h-4 w-4" />} className="card-lift">
                  Get Started Free
                </Button>
              </Link>
              <Link to="/">
                <Button size="lg" variant="outline" className="card-lift">Talk to Us</Button>
              </Link>
            </div>
          </div>
        </div>
      </Reveal>
    </div>
  )
}
