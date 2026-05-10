import { useQuery } from '@tanstack/react-query'
import { Circle } from 'lucide-react'
import { fetchJson } from '../lib/api'
import { cn } from '../lib/cn'

interface HealthResponse {
  status: string
  service: string
}

export function HeaderStatusPill() {
  const { data, isError } = useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: () => fetchJson<HealthResponse>('/api/health'),
    refetchInterval: 30_000,
    retry: 1,
    refetchOnWindowFocus: false,
  })

  const healthy = !isError && data?.status === 'ok'

  return (
    <div
      className="inline-flex items-center gap-1.5 text-xs font-mono text-fg-muted"
      role="status"
      aria-live="polite"
    >
      <Circle
        size={8}
        className={cn(
          'fill-current',
          healthy ? 'text-status-ok' : 'text-status-err',
        )}
      />
      <span>{healthy ? 'API ok' : 'API down'}</span>
    </div>
  )
}
