import { HTMLAttributes } from 'react'

type BadgeVariant = 'default' | 'accent' | 'warning' | 'error' | 'info'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-surface-2 text-fg-muted border-hairline',
  accent: 'bg-accent-muted text-accent border-accent/20',
  warning: 'bg-status-warn/10 text-status-warn border-status-warn/20',
  error: 'bg-status-err/10 text-status-err border-status-err/20',
  info: 'bg-status-info/10 text-status-info border-status-info/20',
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
