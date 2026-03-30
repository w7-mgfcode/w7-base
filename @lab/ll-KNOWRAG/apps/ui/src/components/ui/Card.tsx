import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  selected?: boolean
}

export function Card({ selected, className = '', ...props }: CardProps) {
  return (
    <div
      className={`
        bg-bg-secondary border rounded-lg p-4 transition-colors
        ${selected
          ? 'border-accent bg-accent/5'
          : 'border-border hover:border-border-active'
        }
        ${className}
      `}
      {...props}
    />
  )
}
