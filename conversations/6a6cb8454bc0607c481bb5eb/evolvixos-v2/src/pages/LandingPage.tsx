import { LandingNavBar } from '@/components/landing/LandingNavBar'
import { LandingHero } from '@/components/landing/LandingHero'
import { LandingAIReady } from '@/components/landing/LandingAIReady'
import { LandingFeatures } from '@/components/landing/LandingFeatures'
import { LandingTestimonials } from '@/components/landing/LandingTestimonials'
import { LandingFAQ } from '@/components/landing/LandingFAQ'
import { LandingFooter } from '@/components/landing/LandingFooter'

export function LandingPage() {
  return (
    <div className="bg-bg-base text-text-primary min-h-screen">
      <LandingNavBar />
      <main className="isolate">
        <LandingHero />
        <LandingAIReady />
        <LandingFeatures />
        <LandingTestimonials />
        <LandingFAQ />
      </main>
      <LandingFooter />
    </div>
  )
}
