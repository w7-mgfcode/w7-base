import { InputHTMLAttributes, forwardRef } from 'react'

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  displayValue?: string
}

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ label, displayValue, className = '', ...props }, ref) => {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        {label && <span className="text-xs text-text-secondary whitespace-nowrap">{label}</span>}
        <input
          ref={ref}
          type="range"
          className="flex-1 h-1.5 bg-bg-tertiary rounded-full appearance-none cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
            [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent [&::-webkit-slider-thumb]:cursor-pointer"
          {...props}
        />
        {displayValue && <span className="text-xs text-text-secondary font-mono w-8 text-right">{displayValue}</span>}
      </div>
    )
  }
)
Slider.displayName = 'Slider'
