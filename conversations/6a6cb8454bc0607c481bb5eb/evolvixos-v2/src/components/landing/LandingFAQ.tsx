import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/cn'

interface FAQ {
  id: number
  question: string
  answer: string
  href?: string
}

const faqs: FAQ[] = [
  { id: 1, question: 'What is EvolvixOS?', answer: 'EvolvixOS is an AI Engineering Operating System — a platform that combines autonomous AI agents, real-time monitoring, blockchain integration, and deployment automation to help you build, secure, and operate world-class software systems.' },
  { id: 2, question: 'How does the AI CTO work?', answer: 'The AI CTO agent connects to GPT-4o with full project context — architecture, code, and deployment state. It makes architecture decisions, reviews implementations, and runs weekly security audits automatically, without requiring human approval for each step.' },
  { id: 3, question: 'Is EvolvixOS open source?', answer: 'The platform is built on open-source technologies (React, FastAPI, PostgreSQL, Redis, Docker, Substrate). The core platform code is proprietary, built by Protremix.' },
  { id: 4, question: 'What blockchain does it integrate with?', answer: 'EvolvixOS integrates natively with the Verdis Chain — a carbon-negative blockchain with DPoS consensus, 101 EVM opcodes, native AMM DEX, and carbon credit tracking. The integration includes real-time block data, validator management, and DEX analytics.' },
  { id: 5, question: 'Can I self-host EvolvixOS?', answer: 'Yes. EvolvixOS is designed for self-hosting with Docker containers, systemd services, and Nginx reverse proxy. Full deployment scripts and documentation are included.' },
  { id: 6, question: 'What\'s the pricing model?', answer: 'EvolvixOS is currently in private beta. Contact us for early access and pricing details.' },
]

export function LandingFAQ() {
  const [openId, setOpenId] = useState<number | null>(1)

  return (
    <div className="mx-auto mt-32 max-w-4xl px-6 pb-8 lg:px-8 lg:py-32" id="faq">
      <h2 className="mb-12 text-center text-2xl font-bold tracking-tight text-text-primary">
        Frequently asked questions
      </h2>

      <div className="space-y-4">
        {faqs.map(faq => (
          <div
            key={faq.id}
            className={cn(
              'rounded-lg border px-6 py-2 transition-all',
              openId === faq.id ? 'border-brand/30 bg-bg-surface' : 'border-border bg-bg-surface hover:bg-bg-hover',
            )}
          >
            <button
              onClick={() => setOpenId(openId === faq.id ? null : faq.id)}
              className="flex w-full items-center justify-between py-3 text-left text-base font-semibold text-text-primary"
            >
              {faq.question}
              <ChevronDown className={cn('h-4 w-4 text-text-tertiary transition-transform', openId === faq.id && 'rotate-180')} />
            </button>
            {openId === faq.id && (
              <p className="pb-4 text-sm text-text-secondary leading-7">{faq.answer}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
