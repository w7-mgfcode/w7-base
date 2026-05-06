import { useState } from 'react'
import { useChunks } from '../hooks/useKnowledgeQueries'
import { Spinner } from '../../../components/ui/Spinner'
import { EmptyState } from '../../../components/ui/EmptyState'
import { ChunkCard } from './ChunkCard'
import { Button } from '../../../components/ui/Button'
import { Layers, ChevronLeft, ChevronRight } from 'lucide-react'

interface ChunkListProps {
  sourceId: string
}

const PAGE_SIZE = 50

export function ChunkList({ sourceId }: ChunkListProps) {
  const [offset, setOffset] = useState(0)
  const { data, isLoading } = useChunks(sourceId, offset, PAGE_SIZE)

  if (isLoading) {
    return <div className="flex justify-center py-8"><Spinner /></div>
  }

  if (!data || data.items.length === 0) {
    return <EmptyState icon={<Layers size={40} />} title="No chunks" description="This source has no chunks yet." />
  }

  const totalPages = Math.ceil(data.total / PAGE_SIZE)
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto divide-y divide-border">
        {data.items.map((chunk) => (
          <ChunkCard key={chunk.id} chunk={chunk} />
        ))}
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 py-3 border-t border-hairline text-sm">
          <Button
            variant="ghost"
            size="sm"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
          >
            <ChevronLeft size={14} /> Prev
          </Button>
          <span className="text-fg-muted text-xs">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="ghost"
            size="sm"
            disabled={offset + PAGE_SIZE >= data.total}
            onClick={() => setOffset(offset + PAGE_SIZE)}
          >
            Next <ChevronRight size={14} />
          </Button>
        </div>
      )}
    </div>
  )
}
