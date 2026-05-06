import { useState, useRef, useEffect } from 'react'
import { MoreVertical, RefreshCw, Trash2 } from 'lucide-react'

interface SourceActionsProps {
  onRefresh: () => void
  onDelete: () => void
  isDeleting?: boolean
}

export function SourceActions({ onRefresh, onDelete, isDeleting }: SourceActionsProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div ref={ref} className="relative">
      <button
        onClick={(e) => { e.stopPropagation(); setOpen(!open) }}
        className="p-1 text-fg-subtle hover:text-fg rounded transition-colors cursor-pointer"
      >
        <MoreVertical size={16} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 z-20 bg-surface-1 border border-hairline rounded-lg shadow-xl py-1 min-w-[140px]">
          <button
            onClick={(e) => { e.stopPropagation(); onRefresh(); setOpen(false) }}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-fg hover:bg-surface-2 cursor-pointer"
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); setOpen(false) }}
            disabled={isDeleting}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-status-err hover:bg-status-err/10 cursor-pointer disabled:opacity-50"
          >
            <Trash2 size={14} /> {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      )}
    </div>
  )
}
