import { HTMLAttributes } from 'react'

type BadgeVariant = 'default' | 'accent' | 'warning' | 'error' | 'info'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-bg-tertiary text-text-secondary border-border',
  accent: 'bg-accent-muted text-accent border-accent/20',
  warning: 'bg-warning/10 text-warning border-warning/20',
  error: 'bg-error/10 text-error border-error/20',
  info: 'bg-info/10 text-info border-info/20',
}

export function Badge({ variant = 'default', className = '', ...props }: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center rounded px-2 py-0.5 text-xs font-medium border
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    />
  )
}
