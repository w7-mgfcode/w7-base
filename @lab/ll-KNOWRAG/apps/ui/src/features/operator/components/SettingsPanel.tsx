// SettingsPanel surfaces the chat provider/model the API reported on its
// most recent successful /api/rag/query response. We read the cache key
// populated by useRagQuery rather than calling an endpoint, because no
// /api/config endpoint exists yet. embedding_model is intentionally rendered
// as "—" until that follow-up endpoint lands (out-of-scope per #58).
import { useQueryClient } from '@tanstack/react-query'
import { Card } from '../../../components/ui/Card'
import { RAG_LAST_SUCCESS_KEY } from '../../chat/hooks/useRagQuery'
import type { RagQueryResponse } from '../../chat/types'

interface SettingsRow {
  label: string
  value: string
  hint?: string
}

export function SettingsPanel() {
  const queryClient = useQueryClient()
  const cached = queryClient.getQueryData<RagQueryResponse>(RAG_LAST_SUCCESS_KEY)

  const rows: SettingsRow[] = [
    {
      label: 'chat_provider',
      value: cached?.chat_provider ?? '—',
    },
    {
      label: 'chat_model',
      value: cached?.chat_model ?? '—',
    },
    {
      label: 'embedding_model',
      value: '—',
      hint: 'Pending GET /api/config (filed as deferred follow-up of #58).',
    },
  ]

  return (
    <Card>
      <header className="mb-3">
        <h2 className="text-sm font-semibold text-fg">Active models</h2>
        {!cached ? (
          <p className="mt-1 text-xs text-fg-muted">
            Send a chat query to populate.
          </p>
        ) : null}
      </header>
      <dl className="space-y-2">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-baseline gap-3 text-sm"
          >
            <dt className="font-mono text-xs text-fg-muted w-40 shrink-0">
              {row.label}
            </dt>
            <dd className="font-mono text-fg">{row.value}</dd>
            {row.hint ? (
              <span className="ml-auto text-xs text-fg-muted">{row.hint}</span>
            ) : null}
          </div>
        ))}
      </dl>
    </Card>
  )
}
