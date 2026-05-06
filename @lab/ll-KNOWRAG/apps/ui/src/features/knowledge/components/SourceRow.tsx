import { Source } from '../types'
import { Badge } from '../../../components/ui/Badge'
import { SourceActions } from './SourceActions'

interface SourceRowProps {
  source: Source
  selected: boolean
  onClick: () => void
  onRefresh: () => void
  onDelete: () => void
  isDeleting?: boolean
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export function SourceRow({ source, selected, onClick, onRefresh, onDelete, isDeleting }: SourceRowProps) {
  const tags: string[] = source.metadata?.tags || []

  return (
    <div
      onClick={onClick}
      className={`
        flex items-center gap-3 px-3 py-2.5 border-b border-hairline cursor-pointer transition-colors text-sm
        ${selected ? 'bg-accent/5 border-l-2 border-l-accent' : 'hover:bg-surface-2 border-l-2 border-l-transparent'}
      `}
    >
      <span className="w-2 h-2 rounded-full bg-accent shrink-0" />
      <span className="font-medium truncate min-w-[120px] flex-1">
        {source.source_display_name || source.title || source.source_id}
      </span>
      <span className="text-xs text-fg-muted font-mono truncate max-w-[180px] hidden lg:block">
        {source.source_url}
      </span>
      <span className="text-xs text-fg-muted w-12 text-right">{source.metadata?.page_count ?? '—'}</span>
      <span className="text-xs text-fg-muted w-12 text-right">{source.metadata?.chunk_count ?? '—'}</span>
      <div className="flex gap-1 w-24 hidden md:flex">
        {tags.slice(0, 2).map((tag) => (
          <Badge key={tag} variant="accent">{tag}</Badge>
        ))}
      </div>
      <span className="text-xs text-fg-subtle w-20 text-right hidden md:block">{formatDate(source.updated_at)}</span>
      <SourceActions onRefresh={onRefresh} onDelete={onDelete} isDeleting={isDeleting} />
    </div>
  )
}
