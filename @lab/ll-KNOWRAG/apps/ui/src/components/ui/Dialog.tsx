import { ReactNode } from 'react'
import { Dialog as RadixDialog, VisuallyHidden } from 'radix-ui'
import { X } from 'lucide-react'
import { cn } from '../../lib/cn'

interface DialogProps {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  maxWidth?: string
}

export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'max-w-lg',
}: DialogProps) {
  return (
    <RadixDialog.Root open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=open]:fade-in data-[state=closed]:fade-out" />
        <RadixDialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
            'bg-surface-1 border border-hairline rounded-modal shadow-2xl',
            'w-full mx-4 flex flex-col max-h-[85vh]',
            'focus:outline-none',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
            'data-[state=open]:zoom-in-95 data-[state=closed]:zoom-out-95',
            maxWidth,
          )}
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-hairline">
            <RadixDialog.Title className="text-lg font-semibold">{title}</RadixDialog.Title>
            <RadixDialog.Close
              aria-label="Close dialog"
              className="text-fg-subtle hover:text-fg transition-colors cursor-pointer rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
            >
              <X size={20} />
            </RadixDialog.Close>
          </div>
          {description ? (
            <RadixDialog.Description className="px-6 pt-2 text-sm text-fg-muted">
              {description}
            </RadixDialog.Description>
          ) : (
            <VisuallyHidden.Root>
              <RadixDialog.Description>{title}</RadixDialog.Description>
            </VisuallyHidden.Root>
          )}
          <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>
          {footer && (
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-hairline">
              {footer}
            </div>
          )}
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  )
}
