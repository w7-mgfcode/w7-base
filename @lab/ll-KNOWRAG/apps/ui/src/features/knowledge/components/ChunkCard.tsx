import { useState } from 'react'
import { Chunk } from '../types'
import { Badge } from '../../../components/ui/Badge'
import { ChevronDown, ChevronRight } from 'lucide-react'

interface ChunkCardProps {
  chunk: Chunk
}

export function ChunkCard({ chunk }: ChunkCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="px-5 py-3">
      <div className="flex items-start gap-2">
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-0.5 text-text-tertiary hover:text-text-primary cursor-pointer"
        >
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-text-secondary">Chunk #{chunk.chunk_number}</span>
            <div className="flex gap-1.5">
              {chunk.embedding_model && (
                <Badge variant="default">{chunk.embedding_model}</Badge>
              )}
              {chunk.embedding_dimension && (
                <Badge variant="default">{chunk.embedding_dimension} dim</Badge>
              )}
            </div>
          </div>
          <p className={`text-sm text-text-primary ${expanded ? '' : 'line-clamp-2'}`}>
            {chunk.content}
          </p>
          {chunk.contextual_content && (
            <p className={`text-xs text-text-tertiary mt-1 ${expanded ? '' : 'line-clamp-1'}`}>
              {chunk.contextual_content}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
