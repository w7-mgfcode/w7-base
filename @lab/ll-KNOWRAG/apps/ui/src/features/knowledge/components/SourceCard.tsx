import { Source } from '../types'
import { Card } from '../../../components/ui/Card'
import { Badge } from '../../../components/ui/Badge'
import { SourceActions } from './SourceActions'

interface SourceCardProps {
  source: Source
  selected: boolean
  onClick: () => void
  onRefresh: () => void
  onDelete: () => void
  isDeleting?: boolean
}

function formatRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

export function SourceCard({ source, selected, onClick, onRefresh, onDelete, isDeleting }: SourceCardProps) {
  const tags: string[] = source.metadata?.tags || []
  const pageCount = source.metadata?.page_count ?? '—'
  const chunkCount = source.metadata?.chunk_count ?? '—'

  return (
    <Card selected={selected} className="cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between mb-1">
        <div className="flex items-center gap-2 min-w-0">
          <span className="w-2 h-2 rounded-full bg-accent shrink-0" />
          <span className="text-sm font-medium truncate">
            {source.source_display_name || source.title || source.source_id}
          </span>
        </div>
        <SourceActions onRefresh={onRefresh} onDelete={onDelete} isDeleting={isDeleting} />
      </div>
      {source.source_url && (
        <p className="text-xs text-text-secondary font-mono truncate mb-2 ml-4">
          {source.source_url}
        </p>
      )}
      <div className="flex items-center gap-3 text-xs text-text-secondary ml-4 mb-2">
        <span>Pages: {pageCount}</span>
        <span className="text-border">|</span>
        <span>Chunks: {chunkCount}</span>
      </div>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1 ml-4 mb-2">
          {tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="accent">{tag}</Badge>
          ))}
          {tags.length > 3 && (
            <Badge variant="default">+{tags.length - 3}</Badge>
          )}
        </div>
      )}
      <p className="text-xs text-text-tertiary ml-4">
        Updated {formatRelativeTime(source.updated_at)}
      </p>
    </Card>
  )
}
