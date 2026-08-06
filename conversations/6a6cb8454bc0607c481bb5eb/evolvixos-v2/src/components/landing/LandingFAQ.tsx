import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { Reveal } from './Reveal'
import { cn } from '@/lib/cn'

interface FAQItem {
  question: string
  answer: string
}

const faqs: FAQItem[] = [
  {
    question: 'Can I self-host EvolvixOS?',
    answer: 'Yes. EvolvixOS is designed for self-hosting with Docker containers, systemd services, and automated deployment scripts. The entire stack — frontend, API, workers, database, monitoring — can be deployed on a single server.',
  },
  {
    question: "What's the pricing model?",
    answer: 'EvolvixOS uses a credits-based model. AI agent consultations consume credits, while the core platform (monitoring, deployment, security) is included. Contact us for enterprise pricing.',
  },
  {
    question: 'How does the Verdis Chain integration work?',
    answer: 'EvolvixOS provides a native bridge to the Verdis blockchain via JSON-RPC and gRPC. The integration includes real-time block updates, validator management, DEX analytics, and carbon credit tracking — all accessible through the platform API.',
  },
  {
    question: 'Which AI models power the agents?',
    answer: 'The AI agents use GPT-4o for architecture decisions, code review, and strategic planning. Each agent has specialized system prompts and full project context including code, documentation, and historical decisions.',
  },
]

function FAQAccordion({ item, idx }: { item: FAQItem; idx: number }) {
  const [open, setOpen] = useState(false)

  return (
    <Reveal direction="up" delay={idx * 80} duration={400}>
      <div
        className={cn(
          'rounded-xl border border-border bg-bg-surface overflow-hidden transition-all duration-300 card-lift',
          open && 'border-brand/30',
        )}
      >
        <button
          className="flex w-full items-center justify-between p-5 text-left"
          onClick={() => setOpen(!open)}
        >
          <span className="text-sm font-medium text-text-primary">{item.question}</span>
          <ChevronDown
            className={cn('h-4 w-4 text-text-tertiary transition-transform duration-300', open && 'rotate-180 text-brand')}
          />
        </button>
        <div
          className={cn(
            'grid transition-all duration-300 ease-in-out',
            open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
          )}
        >
          <div className="overflow-hidden">
            <p className="px-5 pb-5 text-sm text-text-secondary leading-relaxed">{item.answer}</p>
          </div>
        </div>
      </div>
    </Reveal>
  )
}

export function LandingFAQ() {
  return (
    <div className="mx-auto max-w-3xl px-6 lg:px-8 mt-24 mb-16">
      <Reveal direction="up" className="text-center mb-8">
        <h2 className="text-3xl font-bold tracking-tight text-text-primary">Frequently asked questions</h2>
        <p className="mt-2 text-text-secondary">Everything you need to know about the platform.</p>
      </Reveal>

      <div className="space-y-3">
        {faqs.map((item, idx) => (
          <FAQAccordion key={idx} item={item} idx={idx} />
        ))}
      </div>
    </div>
  )
}
