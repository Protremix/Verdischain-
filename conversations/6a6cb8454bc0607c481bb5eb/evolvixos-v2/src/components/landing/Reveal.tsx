import { ReactNode, CSSProperties } from 'react'
import { useScrollReveal } from '@/hooks/useScrollReveal'
import { cn } from '@/lib/cn'

type RevealDirection = 'up' | 'down' | 'left' | 'right' | 'scale' | 'fade'

interface RevealProps {
  children: ReactNode
  direction?: RevealDirection
  delay?: number
  duration?: number
  className?: string
  as?: 'div' | 'section' | 'span' | 'li'
}

const directionStyles: Record<RevealDirection, { hidden: CSSProperties; visible: CSSProperties }> = {
  up: {
    hidden: { opacity: 0, transform: 'translateY(40px)' },
    visible: { opacity: 1, transform: 'translateY(0)' },
  },
  down: {
    hidden: { opacity: 0, transform: 'translateY(-40px)' },
    visible: { opacity: 1, transform: 'translateY(0)' },
  },
  left: {
    hidden: { opacity: 0, transform: 'translateX(40px)' },
    visible: { opacity: 1, transform: 'translateX(0)' },
  },
  right: {
    hidden: { opacity: 0, transform: 'translateX(-40px)' },
    visible: { opacity: 1, transform: 'translateX(0)' },
  },
  scale: {
    hidden: { opacity: 0, transform: 'scale(0.92)' },
    visible: { opacity: 1, transform: 'scale(1)' },
  },
  fade: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
}

export function Reveal({
  children,
  direction = 'up',
  delay = 0,
  duration = 600,
  className,
  as: Tag = 'div',
}: RevealProps) {
  const { ref, isVisible } = useScrollReveal<HTMLDivElement>()
  const styles = directionStyles[direction]

  return (
    <Tag
      ref={ref as any}
      className={cn(className)}
      style={{
        ...styles.hidden,
        transition: `opacity ${duration}ms cubic-bezier(0.22, 1, 0.36, 1), transform ${duration}ms cubic-bezier(0.22, 1, 0.36, 1)`,
        transitionDelay: `${delay}ms`,
        ...(isVisible ? styles.visible : {}),
        willChange: 'opacity, transform',
      }}
    >
      {children}
    </Tag>
  )
}
