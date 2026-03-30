import { useState } from 'react'
import { Source } from '../types'
import { Tabs } from '../../../components/ui/Tabs'
import { Button } from '../../../components/ui/Button'
import { SourceInfoPanel } from './SourceInfoPanel'
import { PageList } from './PageList'
import { ChunkList } from './ChunkList'
import { CrawlProgress } from './CrawlProgress'
import { usePages, useChunks } from '../hooks/useKnowledgeQueries'
import { ArrowLeft, RefreshCw } from 'lucide-react'

interface SourceDetailProps {
  source: Source
  activeCrawlIds: string[]
  onCrawlComplete: (crawlId: string) => void
  onRefresh?: (sourceId: string) => void
  onBack: () => void
}

export function SourceDetail({ source, activeCrawlIds, onCrawlComplete, onRefresh, onBack }: SourceDetailProps) {
  const [activeTab, setActiveTab] = useState('info')
  const { data: pages = [] } = usePages(source.source_id)
  const { data: chunkData } = useChunks(activeTab === 'chunks' ? source.source_id : undefined)

  const tabs = [
    { id: 'info', label: 'Info' },
    { id: 'pages', label: `Pages (${pages.length})` },
    { id: 'chunks', label: `Chunks (${chunkData?.total ?? '—'})` },
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-3 border-b border-border">
        <button onClick={onBack} className="lg:hidden text-text-secondary hover:text-text-primary cursor-pointer">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <h2 className="text-base font-semibold truncate">
            {source.source_display_name || source.title || source.source_id}
          </h2>
          {source.source_url && (
            <p className="text-xs text-text-secondary font-mono truncate">{source.source_url}</p>
          )}
        </div>
        <Button variant="secondary" size="sm" onClick={() => onRefresh?.(source.source_id)}>
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      {/* Active Crawls */}
      {activeCrawlIds.map((id) => (
        <CrawlProgress key={id} crawlId={id} onComplete={() => onCrawlComplete(id)} />
      ))}

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab}>
        <div className="overflow-y-auto h-full">
          {activeTab === 'info' && <SourceInfoPanel source={source} />}
          {activeTab === 'pages' && <PageList sourceId={source.source_id} />}
          {activeTab === 'chunks' && <ChunkList sourceId={source.source_id} />}
        </div>
      </Tabs>
    </div>
  )
}
