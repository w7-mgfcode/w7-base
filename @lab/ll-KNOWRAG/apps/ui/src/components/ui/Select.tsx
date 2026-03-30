import { SelectHTMLAttributes, forwardRef } from 'react'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={`
          bg-bg-tertiary border border-border rounded-md px-3 py-2 text-sm
          text-text-primary
          focus:border-accent focus:ring-1 focus:ring-accent/30 focus:outline-none
          disabled:opacity-50 disabled:cursor-not-allowed
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
    )
  }
)
Select.displayName = 'Select'
