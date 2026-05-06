import { useState } from 'react'
import { usePages } from '../hooks/useKnowledgeQueries'
import { Spinner } from '../../../components/ui/Spinner'
import { EmptyState } from '../../../components/ui/EmptyState'
import { PageViewer } from './PageViewer'
import { ChevronRight, FileText } from 'lucide-react'

interface PageListProps {
  sourceId: string
}

export function PageList({ sourceId }: PageListProps) {
  const { data: pages = [], isLoading } = usePages(sourceId)
  const [expandedPageId, setExpandedPageId] = useState<string | null>(null)

  if (isLoading) {
    return <div className="flex justify-center py-8"><Spinner /></div>
  }

  if (pages.length === 0) {
    return <EmptyState icon={<FileText size={40} />} title="No pages" description="This source has no ingested pages yet." />
  }

  return (
    <div className="divide-y divide-border">
      {pages.map((page) => (
        <div key={page.id}>
          <button
            onClick={() => setExpandedPageId(expandedPageId === page.id ? null : page.id)}
            className="w-full flex items-center gap-3 px-5 py-3 text-left hover:bg-surface-2 transition-colors cursor-pointer"
          >
            <ChevronRight
              size={14}
              className={`text-fg-subtle transition-transform ${expandedPageId === page.id ? 'rotate-90' : ''}`}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{page.section_title || page.url}</p>
              <p className="text-xs text-fg-muted font-mono truncate">{page.url}</p>
            </div>
            <span className="text-xs text-fg-subtle whitespace-nowrap">
              {page.word_count.toLocaleString()} words
            </span>
          </button>
          {expandedPageId === page.id && (
            <PageViewer page={page} />
          )}
        </div>
      ))}
    </div>
  )
}
