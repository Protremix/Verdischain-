import { Link } from 'react-router-dom'
import { ArrowRight, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/Button'

const navItems = [
  { name: 'Features', to: '/#features' },
  { name: 'AI Agents', to: '/#ai-agents' },
  { name: 'Pricing', to: '/#pricing' },
  { name: 'Docs', to: '/docs' },
]

export function LandingNavBar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const handler = () => setIsScrolled(window.scrollY > 0)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
      <div className={cn(
        'transition-all duration-300',
        isScrolled
          ? 'mx-4 mt-2 rounded-2xl bg-bg-surface/90 border border-border shadow-lg backdrop-blur-xl md:mx-16'
          : 'bg-bg-base/80 border-b border-border backdrop-blur-lg'
      )}>
        <nav className={cn('flex items-center justify-between transition-all duration-300', isScrolled ? 'px-5 py-3' : 'px-6 py-3 lg:px-10')}>
          <div className="flex items-center gap-8">
            {/* BIG LOGO - prominent at top of all pages */}
            <Link to="/" className="flex items-center gap-2.5 group">
              <img
                src="/evolvixos-logo.png"
                alt="EvolvixOS"
                className="h-12 w-auto transition-transform duration-300 group-hover:scale-105"
                style={{ maxHeight: '48px' }}
              />
            </Link>
            <ul className="hidden lg:flex items-center gap-6 ml-2">
              {navItems.map(item => (
                <li key={item.name}>
                  <a
                    href={item.to}
                    className="text-sm text-text-secondary hover:text-text-primary transition-colors relative after:absolute after:bottom-[-4px] after:left-0 after:h-0.5 after:w-0 after:bg-brand after:transition-all after:duration-300 hover:after:w-full"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div className="hidden lg:flex items-center gap-3">
            <Link to="/settings" className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
              Log in
            </Link>
            <Button size="sm" icon={<ArrowRight className="h-3.5 w-3.5" />} className="card-lift">
              Get Started
            </Button>
          </div>

          <button className="lg:hidden h-10 w-10 flex items-center justify-center rounded-lg hover:bg-bg-hover" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X className="h-5 w-5 text-text-primary" /> : <Menu className="h-5 w-5 text-text-primary" />}
          </button>
        </nav>

        {mobileOpen && (
          <div className="lg:hidden border-t border-border p-4 space-y-2 animate-fade-in">
            {navItems.map(item => (
              <a key={item.name} href={item.to} onClick={() => setMobileOpen(false)} className="block py-2 text-sm text-text-secondary hover:text-text-primary">
                {item.name}
              </a>
            ))}
            <Link to="/settings" className="block py-2 text-sm text-text-secondary hover:text-text-primary">Log in</Link>
            <Link to="/" className="block py-2 text-sm font-medium text-brand">Get Started →</Link>
          </div>
        )}
      </div>
    </header>
  )
}
