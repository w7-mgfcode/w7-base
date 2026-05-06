import { InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className = '', ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={`
          w-full bg-surface-2 border border-hairline rounded-md px-3 py-2 text-sm
          text-fg placeholder:text-fg-subtle
          focus:border-accent focus:ring-1 focus:ring-accent/30 focus:outline-none
          disabled:opacity-50 disabled:cursor-not-allowed
          ${className}
        `}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'
