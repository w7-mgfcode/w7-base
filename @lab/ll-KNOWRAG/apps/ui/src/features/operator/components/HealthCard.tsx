import { Circle } from 'lucide-react'
import { Card } from '../../../components/ui/Card'
import { cn } from '../../../lib/cn'
import { useHealth } from '../hooks/useOperatorQueries'

const RELATIVE_FORMAT = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

function relativeFromMillis(timestamp: number | undefined): string {
  if (!timestamp) return '—'
  const seconds = Math.round((timestamp - Date.now()) / 1000)
  return RELATIVE_FORMAT.format(seconds, 'second')
}

export function HealthCard() {
  const { data, isError, dataUpdatedAt, isLoading } = useHealth()
  const healthy = !isError && data?.status === 'ok'
  const serviceName = data?.service ?? 'knowrag-api'
  const lastChecked = isLoading ? 'never' : relativeFromMillis(dataUpdatedAt)

  return (
    <Card>
      <header className="mb-3">
        <h2 className="text-sm font-semibold text-fg">System Health</h2>
      </header>
      <ul className="space-y-2">
        <li className="flex items-center gap-3 text-sm">
          <Circle
            size={10}
            className={cn(
              'fill-current shrink-0',
              healthy ? 'text-status-ok' : 'text-status-err',
            )}
            aria-label={healthy ? 'healthy' : 'unhealthy'}
          />
          <span className="font-mono text-fg">{serviceName}</span>
          <span className="ml-auto text-xs text-fg-muted" data-testid="last-checked">
            checked {lastChecked}
          </span>
        </li>
      </ul>
    </Card>
  )
}
