import { LandingNavBar } from '@/components/landing/LandingNavBar'
import { LandingHero } from '@/components/landing/LandingHero'
import { LandingTrustedBy } from '@/components/landing/LandingTrustedBy'
import { LandingAIReady } from '@/components/landing/LandingAIReady'
import { LandingProductDemo } from '@/components/landing/LandingProductDemo'
import { LandingFeatures } from '@/components/landing/LandingFeatures'
import { LandingTestimonials } from '@/components/landing/LandingTestimonials'
import { LandingCTA } from '@/components/landing/LandingCTA'
import { LandingFAQ } from '@/components/landing/LandingFAQ'
import { LandingFooter } from '@/components/landing/LandingFooter'

export function LandingPage() {
  return (
    <div className="bg-bg-base text-text-primary min-h-screen">
      <LandingNavBar />
      <main className="isolate">
        <LandingHero />
        <LandingTrustedBy />
        <LandingAIReady />
        <LandingProductDemo />
        <LandingFeatures />
        <LandingTestimonials />
        <LandingCTA />
        <LandingFAQ />
      </main>
      <LandingFooter />
    </div>
  )
}
