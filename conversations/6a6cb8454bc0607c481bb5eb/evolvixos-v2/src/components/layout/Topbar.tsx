import { Search, Bell, Sun, Moon, Menu, Command } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

interface TopbarProps {
  onMenuClick: () => void
}

export function Topbar({ onMenuClick }: TopbarProps) {
  const { theme, toggle } = useTheme()

  return (
    <header className="sticky top-0 z-30 h-16 flex items-center gap-3 px-4 lg:px-6
      bg-bg-base/80 backdrop-blur-xl border-b border-border">
      {/* Mobile menu */}
      <button
        onClick={onMenuClick}
        className="lg:hidden h-9 w-9 flex items-center justify-center rounded-lg hover:bg-bg-hover transition-colors"
      >
        <Menu className="h-5 w-5 text-text-secondary" />
      </button>

      {/* Search / Command */}
      <div className="flex-1 max-w-xl">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
          <input
            type="text"
            placeholder="Search or jump to..."
            className="w-full h-9 pl-9 pr-16 rounded-lg bg-bg-input border border-border
              text-sm text-text-primary placeholder:text-text-tertiary
              focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/15
              transition-all"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:flex items-center gap-0.5
            px-1.5 py-0.5 rounded text-2xs font-medium text-text-tertiary bg-bg-hover border border-border">
            <Command className="h-3 w-3" />K
          </kbd>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        <button
          onClick={toggle}
          className="h-9 w-9 flex items-center justify-center rounded-lg hover:bg-bg-hover transition-colors text-text-secondary hover:text-text-primary"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
        </button>

        <button
          className="relative h-9 w-9 flex items-center justify-center rounded-lg hover:bg-bg-hover transition-colors text-text-secondary hover:text-text-primary"
          aria-label="Notifications"
        >
          <Bell className="h-4.5 w-4.5" />
          <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-brand ring-2 ring-bg-base" />
        </button>

        <div className="w-px h-6 bg-border mx-1 hidden sm:block" />

        <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-lg bg-success/10 text-success">
          <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
          <span className="text-xs font-medium">All systems operational</span>
        </div>
      </div>
    </header>
  )
}
