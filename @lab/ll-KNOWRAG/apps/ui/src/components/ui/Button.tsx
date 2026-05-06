import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/cn'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-control font-medium transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface-0',
  {
    variants: {
      variant: {
        primary: 'bg-accent text-white hover:bg-accent-strong',
        secondary: 'bg-surface-2 text-fg border border-hairline hover:border-hairline-strong',
        ghost: 'text-fg-muted hover:bg-surface-2 hover:text-fg',
        destructive: 'bg-status-err/10 text-status-err border border-status-err/20 hover:bg-status-err/20',
      },
      size: {
        sm: 'px-2.5 py-1 text-xs',
        md: 'px-3.5 py-2 text-sm',
        lg: 'px-5 py-2.5 text-sm',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  },
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, size, className, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
)
Button.displayName = 'Button'
