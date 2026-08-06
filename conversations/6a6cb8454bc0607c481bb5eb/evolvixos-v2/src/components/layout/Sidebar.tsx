import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, FolderGit2, Bot, BookOpen, Activity,
  Shield, Settings, BarChart3, FileText, Rocket, Network,
  ChevronLeft
} from 'lucide-react'
import { cn } from '@/lib/cn'

const navItems = [
  { section: 'Overview', items: [
    { to: '/app', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/app/analytics', label: 'Analytics', icon: BarChart3 },
    { to: '/app/activity', label: 'Activity', icon: Activity },
  ]},
  { section: 'Engineering', items: [
    { to: '/app/projects', label: 'Projects', icon: FolderGit2 },
    { to: '/app/repositories', label: 'Repositories', icon: Network },
    { to: '/app/deployments', label: 'Deployments', icon: Rocket },
  ]},
  { section: 'AI', items: [
    { to: '/app/ai-workspace', label: 'AI Workspace', icon: Bot },
    { to: '/app/knowledge', label: 'Knowledge', icon: BookOpen },
  ]},
  { section: 'Platform', items: [
    { to: '/app/monitoring', label: 'Monitoring', icon: Activity },
    { to: '/app/security', label: 'Security', icon: Shield },
    { to: '/app/docs', label: 'Docs', icon: FileText },
    { to: '/app/settings', label: 'Settings', icon: Settings },
  ]},
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  mobileOpen: boolean
  onMobileClose: () => void
}

export function Sidebar({ collapsed, onToggle, mobileOpen, onMobileClose }: SidebarProps) {
  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" onClick={onMobileClose} />
      )}

      <aside className={cn(
        'fixed left-0 top-0 z-50 h-screen flex flex-col bg-bg-surface border-r border-border transition-all duration-300 ease-out',
        collapsed ? 'w-[60px]' : 'w-[240px]',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      )}>
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-border">
          <NavLink to="/" className="flex items-center gap-2 min-w-0">
            {collapsed
              ? <img src="/evolvixos-icon.png" alt="EvolvixOS" className="h-8 w-8 object-contain flex-shrink-0" />
              : <img src="/evolvixos-logo.png" alt="EvolvixOS" className="h-7 w-auto" />}
          </NavLink>
        </div>

        {/* Collapse toggle */}
        <button
          onClick={onToggle}
          className="hidden lg:flex absolute -right-3 top-20 h-6 w-6 items-center justify-center rounded-full bg-bg-elevated border border-border text-text-tertiary hover:text-text-primary hover:border-border-strong transition-all z-10"
        >
          <ChevronLeft className={cn('h-3.5 w-3.5 transition-transform', collapsed && 'rotate-180')} />
        </button>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
          {navItems.map(group => (
            <div key={group.section}>
              {!collapsed && <p className="px-3 mb-1.5 text-2xs font-semibold uppercase tracking-wider text-text-tertiary">{group.section}</p>}
              <div className="space-y-0.5">
                {group.items.map(item => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/app'}
                    onClick={onMobileClose}
                    className={({ isActive }) => cn(
                      'flex items-center gap-3 rounded-lg px-3 h-9 text-sm font-medium transition-all',
                      collapsed && 'justify-center px-0',
                      isActive ? 'bg-brand/10 text-brand' : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover',
                    )}
                  >
                    <item.icon className="h-4 w-4 flex-shrink-0" strokeWidth={2} />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-border p-3">
          <NavLink to="/app/settings" className={cn('flex items-center gap-3 rounded-lg p-2 hover:bg-bg-hover transition-colors cursor-pointer', collapsed && 'justify-center')}>
            <div className="h-8 w-8 rounded-full bg-brand/10 text-brand flex items-center justify-center text-xs font-medium flex-shrink-0">RG</div>
            {!collapsed && (
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-text-primary truncate">Rojs Gordons</p>
                <p className="text-xs text-text-tertiary truncate">CEO · Protremix</p>
              </div>
            )}
          </NavLink>
        </div>
      </aside>
    </>
  )
}
