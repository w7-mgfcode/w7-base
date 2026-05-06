import { useState, useMemo } from 'react'
import { Grid3x3, List, Search } from 'lucide-react'
import { Source } from '../types'
import { Input } from '../../../components/ui/Input'
import { Select } from '../../../components/ui/Select'
import { SourceCard } from './SourceCard'
import { SourceRow } from './SourceRow'
import { EmptyState } from '../../../components/ui/EmptyState'
import { Spinner } from '../../../components/ui/Spinner'
import { Button } from '../../../components/ui/Button'

type ViewMode = 'grid' | 'table'
type TypeFilter = 'all' | 'crawled' | 'uploaded'

interface SourceListProps {
  sources: Source[]
  isLoading: boolean
  selectedSourceId: string | null
  deletingSourceId: string | null
  onSelect: (source: Source) => void
  onRefresh: (sourceId: string) => void
  onDelete: (sourceId: string) => void
  onAddKnowledge: () => void
}

export function SourceList({
  sources, isLoading, selectedSourceId, deletingSourceId,
  onSelect, onRefresh, onDelete, onAddKnowledge,
}: SourceListProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const filtered = useMemo(() => {
    let result = sources
    if (typeFilter === 'crawled') {
      result = result.filter((s) => s.source_url && !s.metadata?.upload)
    } else if (typeFilter === 'uploaded') {
      result = result.filter((s) => s.metadata?.upload)
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      result = result.filter((s) =>
        (s.source_display_name || '').toLowerCase().includes(q) ||
        (s.title || '').toLowerCase().includes(q) ||
        (s.source_url || '').toLowerCase().includes(q) ||
        s.source_id.toLowerCase().includes(q)
      )
    }
    return result
  }, [sources, typeFilter, searchQuery])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size={24} />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Filter bar */}
      <div className="flex items-center gap-2 p-3 border-b border-border">
        <Select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
          className="w-28 text-xs"
        >
          <option value="all">All</option>
          <option value="crawled">Crawled</option>
          <option value="uploaded">Uploaded</option>
        </Select>
        <div className="relative flex-1">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-tertiary" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter sources..."
            className="pl-8 text-xs"
          />
        </div>
        <div className="flex border border-border rounded-md overflow-hidden">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 cursor-pointer ${viewMode === 'grid' ? 'bg-bg-tertiary text-text-primary' : 'text-text-tertiary hover:text-text-secondary'}`}
          >
            <Grid3x3 size={14} />
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`p-1.5 cursor-pointer ${viewMode === 'table' ? 'bg-bg-tertiary text-text-primary' : 'text-text-tertiary hover:text-text-secondary'}`}
          >
            <List size={14} />
          </button>
        </div>
      </div>

      {/* Source list */}
      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <EmptyState
            title="No sources found"
            description={sources.length === 0
              ? 'Add your first knowledge source to get started.'
              : 'No sources match your current filters.'
            }
            action={sources.length === 0 ? (
              <Button onClick={onAddKnowledge}>+ Add Knowledge</Button>
            ) : undefined}
          />
        ) : viewMode === 'grid' ? (
          <div className="p-3 space-y-2">
            {filtered.map((source) => (
              <SourceCard
                key={source.source_id}
                source={source}
                selected={selectedSourceId === source.source_id}
                onClick={() => onSelect(source)}
                onRefresh={() => onRefresh(source.source_id)}
                onDelete={() => onDelete(source.source_id)}
                isDeleting={deletingSourceId === source.source_id}
              />
            ))}
          </div>
        ) : (
          <div>
            {filtered.map((source) => (
              <SourceRow
                key={source.source_id}
                source={source}
                selected={selectedSourceId === source.source_id}
                onClick={() => onSelect(source)}
                onRefresh={() => onRefresh(source.source_id)}
                onDelete={() => onDelete(source.source_id)}
                isDeleting={deletingSourceId === source.source_id}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
