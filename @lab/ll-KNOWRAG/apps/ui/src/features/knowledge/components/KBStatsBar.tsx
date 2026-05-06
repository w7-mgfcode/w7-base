import { useKBSummary } from '../hooks/useKnowledgeQueries'
import { Activity } from 'lucide-react'

interface KBStatsBarProps {
  activeCrawlCount: number
  onActiveCrawlClick?: () => void
}

function StatCell({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="flex flex-col items-center px-5 border-r border-hairline last:border-r-0">
      <span className="text-2xl font-bold text-fg">{value}</span>
      <span className="text-xs text-fg-muted">{label}</span>
    </div>
  )
}

export function KBStatsBar({ activeCrawlCount, onActiveCrawlClick }: KBStatsBarProps) {
  const { data: summary } = useKBSummary()

  return (
    <div className="flex items-center bg-surface-1 border-b border-hairline px-4 h-12">
      <div className="flex items-center flex-1">
        <StatCell value={summary?.total_sources ?? '—'} label="Sources" />
        <StatCell value={summary?.total_pages ?? '—'} label="Pages" />
        <StatCell value={summary?.total_chunks ?? '—'} label="Chunks" />
      </div>
      {activeCrawlCount > 0 && (
        <button
          onClick={onActiveCrawlClick}
          className="flex items-center gap-2 text-xs text-status-warn cursor-pointer hover:opacity-80"
        >
          <span className="w-2 h-2 rounded-full bg-status-warn animate-pulse-dot" />
          <Activity size={14} />
          <span>{activeCrawlCount} crawl{activeCrawlCount > 1 ? 's' : ''} active</span>
        </button>
      )}
    </div>
  )
}
