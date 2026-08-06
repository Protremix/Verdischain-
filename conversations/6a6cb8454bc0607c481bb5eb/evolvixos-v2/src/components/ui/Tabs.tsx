import { useState } from 'react'
import { cn } from '@/lib/cn'

interface TabsProps {
  tabs: { label: string; value: string; icon?: React.ReactNode }[]
  defaultValue?: string
  onChange?: (value: string) => void
  className?: string
}

export function Tabs({ tabs, defaultValue, onChange, className }: TabsProps) {
  const [active, setActive] = useState(defaultValue ?? tabs[0]?.value)

  const handleChange = (value: string) => {
    setActive(value)
    onChange?.(value)
  }

  return (
    <div className={cn('flex items-center gap-1 border-b border-border', className)}>
      {tabs.map(tab => (
        <button
          key={tab.value}
          onClick={() => handleChange(tab.value)}
          className={cn(
            'relative inline-flex items-center gap-2 px-3 py-2.5 text-sm font-medium transition-colors',
            'hover:text-text-primary',
            active === tab.value ? 'text-text-primary' : 'text-text-tertiary'
          )}
        >
          {tab.icon}
          {tab.label}
          {active === tab.value && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand rounded-t-full" />
          )}
        </button>
      ))}
    </div>
  )
}
