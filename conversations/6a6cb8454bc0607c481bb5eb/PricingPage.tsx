import { Link } from 'react-router-dom'
import { Check, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { LandingNavBar } from '@/components/landing/LandingNavBar'
import { LandingFooter } from '@/components/landing/LandingFooter'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for individuals exploring AI-powered engineering',
    features: [
      '5 AI agent consultations per month',
      'Access to AI CTO agent',
      'Community support',
      '1 project',
      'Basic monitoring dashboard',
      'GitHub integration',
    ],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: 'per month',
    description: 'For teams shipping software with AI assistance',
    features: [
      'Unlimited AI agent consultations',
      'All 5 AI agents (CTO, Architect, Planner, Reviewer, Developer)',
      'Priority support',
      'Unlimited projects',
      'Advanced monitoring + alerting',
      'Security scanning',
      'Deployment automation',
      'Custom AI prompts',
    ],
    cta: 'Start 14-Day Trial',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    description: 'For organizations needing full AI engineering infrastructure',
    features: [
      'Everything in Pro',
      'SSO/SAML integration',
      'RBAC with custom roles',
      'GDPR compliance tools',
      'Dedicated infrastructure',
      'SLA guarantee (99.9%)',
      'Custom AI model fine-tuning',
      'On-premise deployment option',
      'Dedicated support engineer',
    ],
    cta: 'Book a Demo',
    highlighted: false,
  },
]

export function PricingPage() {
  return (
    <div className='bg-bg-base text-text-primary min-h-screen'>
      <LandingNavBar />
      <main className='isolate pt-32 pb-20'>
        <div className='mx-auto max-w-7xl px-6 lg:px-8'>
          <div className='text-center'>
            <h1 className='text-4xl font-bold tracking-tight text-text-primary'>
              Simple, transparent pricing
            </h1>
            <p className='mt-4 text-lg text-text-secondary max-w-2xl mx-auto'>
              Start free. Upgrade when you need more. Cancel anytime.
              Credits-based model — you only pay for what you use.
            </p>
          </div>

          <div className='mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8'>
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-2xl border p-8 ${
                  plan.highlighted
                    ? 'border-brand bg-bg-surface shadow-xl shadow-brand/5 scale-105'
                    : 'border-border bg-bg-surface'
                }`}
              >
                {plan.highlighted && (
                  <div className='absolute -top-3 left-1/2 -translate-x-1/2'>
                    <span className='rounded-full bg-brand px-4 py-1 text-xs font-semibold text-white'>
                      Most Popular
                    </span>
                  </div>
                )}
                <h3 className='text-xl font-semibold text-text-primary'>{plan.name}</h3>
                <p className='mt-1 text-sm text-text-tertiary'>{plan.description}</p>
                <div className='mt-4 flex items-baseline gap-1'>
                  <span className='text-4xl font-bold text-text-primary'>{plan.price}</span>
                  <span className='text-sm text-text-tertiary'>/{plan.period}</span>
                </div>
                <Link to={plan.name === 'Enterprise' ? '/support' : '/register'}>
                  <Button
                    className='w-full mt-6'
                    variant={plan.highlighted ? 'primary' : 'secondary'}
                    size='md'
                  >
                    {plan.cta}
                    <ArrowRight className='h-4 w-4 ml-2' />
                  </Button>
                </Link>
                <ul className='mt-6 space-y-3'>
                  {plan.features.map((feature) => (
                    <li key={feature} className='flex items-start gap-2.5 text-sm text-text-secondary'>
                      <Check className='h-4 w-4 text-brand flex-shrink-0 mt-0.5' />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className='mt-16 text-center'>
            <p className='text-sm text-text-tertiary'>
              All plans include SSL encryption, automated backups, and 24/7 AI agent monitoring.
              No credit card required for the Free plan.
            </p>
          </div>
        </div>
      </main>
      <LandingFooter />
    </div>
  )
}
