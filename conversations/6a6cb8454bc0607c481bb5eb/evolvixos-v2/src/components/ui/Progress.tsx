import { cn } from '@/lib/cn'

interface ProgressProps {
  value: number
  max?: number
  size?: 'sm' | 'md'
  color?: 'brand' | 'success' | 'warning' | 'danger'
  className?: string
}

const colors = {
  brand: 'bg-brand',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
}

const sizes = {
  sm: 'h-1',
  md: 'h-2',
}

export function Progress({ value, max = 100, size = 'md', color = 'brand', className }: ProgressProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className={cn('w-full rounded-full bg-bg-hover overflow-hidden', sizes[size], className)}>
      <div
        className={cn('h-full rounded-full transition-all duration-500 ease-out', colors[color])}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
