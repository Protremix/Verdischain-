import { Link } from 'react-router-dom'
import { Github } from 'lucide-react'

const footerNav = {
  Product: [
    { name: 'Features', href: '/#features' },
    { name: 'AI Workspace', href: '/#ai-agents' },
    { name: 'Monitoring', href: '/' },
    { name: 'Security', href: '/' },
  ],
  Platform: [
    { name: 'API Docs', href: '/docs' },
    { name: 'Pricing', href: '/#pricing' },
    { name: 'Changelog', href: '/' },
    { name: 'Status', href: '/' },
  ],
  Company: [
    { name: 'About', href: '#' },
    { name: 'Privacy', href: '#' },
    { name: 'Terms', href: '#' },
    { name: 'Contact', href: '/support' },
  ],
}

export function LandingFooter() {
  return (
    <footer className="border-t border-border mt-16">
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16">
        <div className="flex flex-col lg:flex-row justify-between gap-12">
          {/* Brand - bigger logo */}
          <div className="max-w-sm">
            <Link to="/" className="flex items-center gap-2.5 mb-4 group">
              <img
                src="/evolvixos-logo.png"
                alt="EvolvixOS"
                className="h-10 w-auto transition-transform duration-300 group-hover:scale-105"
                style={{ maxHeight: '40px' }}
              />
            </Link>
            <p className="text-sm text-text-tertiary leading-relaxed">
              The AI Engineering Operating System for building, operating, and securing
              world-class software systems.
            </p>
            <a href="https://github.com/evolvixos" className="inline-flex items-center gap-2 mt-4 text-sm text-text-secondary hover:text-text-primary transition-colors">
              <Github className="h-4 w-4" />
              github.com/evolvixos
            </a>
          </div>

          {/* Nav columns */}
          <div className="flex gap-16">
            {Object.entries(footerNav).map(([section, items]) => (
              <div key={section}>
                <h3 className="text-sm font-semibold text-text-primary mb-4">{section}</h3>
                <ul className="space-y-3">
                  {items.map(item => (
                    <li key={item.name}>
                      <a href={item.href} className="text-sm text-text-tertiary hover:text-text-primary transition-colors">
                        {item.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-border flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-text-tertiary">© 2026 EvolvixOS by Protremix. All rights reserved.</p>
          <p className="text-xs text-text-tertiary">Built with React, Tailwind CSS, and autonomous AI agents.</p>
        </div>
      </div>
    </footer>
  )
}
