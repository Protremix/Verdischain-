import { forwardRef } from 'react'
import { cn } from '@/lib/cn'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  icon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, icon, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="mb-1.5 block text-xs font-medium text-text-secondary">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'w-full h-10 rounded-lg bg-bg-input border border-border px-3 text-sm text-text-primary',
              'placeholder:text-text-tertiary transition-all duration-150',
              'hover:border-border-strong focus:border-brand focus:ring-2 focus:ring-brand/20 focus:outline-none',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              icon && 'pl-9',
              error && 'border-danger focus:border-danger focus:ring-danger/20',
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 text-xs text-danger">{error}</p>
        )}
        {hint && !error && (
          <p className="mt-1.5 text-xs text-text-tertiary">{hint}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
