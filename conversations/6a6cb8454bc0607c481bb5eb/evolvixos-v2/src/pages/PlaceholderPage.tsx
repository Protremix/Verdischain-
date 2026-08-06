import { cn } from '@/lib/cn'

interface PlaceholderProps {
  title: string
  description?: string
  icon?: React.ReactNode
}

export function PlaceholderPage({ title, description, icon }: PlaceholderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
      <div className="h-16 w-16 rounded-2xl bg-bg-surface border border-border flex items-center justify-center mb-4">
        {icon}
      </div>
      <h1 className="text-xl font-semibold text-text-primary">{title}</h1>
      <p className="mt-1 text-sm text-text-secondary text-center max-w-sm">
        {description || 'This page is under construction. Full functionality coming soon.'}
      </p>
    </div>
  )
}
