import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  selected?: boolean
}

export function Card({ selected, className = '', ...props }: CardProps) {
  return (
    <div
      className={`
        bg-surface-1 border rounded-lg p-4 transition-colors
        ${selected
          ? 'border-accent bg-accent/5'
          : 'border-hairline hover:border-hairline-strong'
        }
        ${className}
      `}
      {...props}
    />
  )
}
