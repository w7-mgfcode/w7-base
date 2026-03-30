import { useEffect, useRef } from 'react'
import { useCrawlProgress, useStopCrawl } from '../hooks/useKnowledgeQueries'
import { Button } from '../../../components/ui/Button'
import { Spinner } from '../../../components/ui/Spinner'
import { Square } from 'lucide-react'

interface CrawlProgressProps {
  crawlId: string
  onComplete: () => void
}

export function CrawlProgress({ crawlId, onComplete }: CrawlProgressProps) {
  const { data: progress } = useCrawlProgress(crawlId)
  const stopCrawl = useStopCrawl()
  const notifiedRef = useRef(false)

  const isTerminal = progress && ['completed', 'failed', 'cancelled'].includes(progress.status)
  const pct = progress && progress.total_tasks > 0
    ? Math.round((progress.completed_tasks / progress.total_tasks) * 100)
    : 0

  useEffect(() => {
    if (isTerminal && !notifiedRef.current) {
      notifiedRef.current = true
      const t = setTimeout(onComplete, 3000)
      return () => clearTimeout(t)
    }
  }, [isTerminal, onComplete])

  if (!progress) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-bg-secondary border-b border-border">
        <Spinner size={14} />
        <span className="text-xs text-text-secondary">Loading crawl status...</span>
      </div>
    )
  }

  return (
    <div className="px-4 py-3 bg-bg-secondary border-b border-border">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {!isTerminal && <Spinner size={14} />}
          <span className="text-sm font-medium">
            {isTerminal ? `Crawl ${progress.status}` : 'Crawling...'}
          </span>
        </div>
        {!isTerminal && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => stopCrawl.mutate(crawlId)}
            disabled={stopCrawl.isPending}
          >
            <Square size={12} /> Stop
          </Button>
        )}
      </div>

      <div className="w-full h-1.5 bg-bg-tertiary rounded-full overflow-hidden mb-2">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            progress.status === 'failed' ? 'bg-error' :
            isTerminal ? 'bg-accent' : 'bg-warning'
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-text-secondary">
        <span>{progress.completed_tasks}/{progress.total_tasks} pages</span>
        {progress.current_task_url && !isTerminal && (
          <span className="font-mono truncate max-w-[300px]">{progress.current_task_url}</span>
        )}
        {progress.failed_tasks > 0 && (
          <span className="text-error">Failed: {progress.failed_tasks}</span>
        )}
      </div>
      {progress.error && (
        <p className="text-xs text-error mt-1">{progress.error}</p>
      )}
    </div>
  )
}
