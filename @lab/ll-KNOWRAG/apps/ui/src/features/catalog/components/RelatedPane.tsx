import { useRelatedArtifacts } from '../hooks/useCatalogQueries'
import { RelatedArtifact } from '../types'
import { Spinner } from '../../../components/ui/Spinner'

interface RelatedPaneProps {
  path: string
  visibility?: 'public' | 'private'
  k?: number
  onSelect: (path: string) => void
}

export function RelatedPane({ path, visibility = 'public', k = 5, onSelect }: RelatedPaneProps) {
  const { data, isLoading, isError, error } = useRelatedArtifacts(path, k, visibility)

  return (
    <aside className="w-[300px] shrink-0 border-l border-hairline bg-surface-1 p-4 overflow-y-auto">
      <h3 className="text-xs uppercase tracking-wide text-fg-subtle mb-3">
        Related
      </h3>
      {isLoading && (
        <div className="flex items-center gap-2 text-xs text-fg-muted">
          <Spinner size={14} />
          <span>Finding similar artifacts…</span>
        </div>
      )}
      {isError && (
        <p className="text-xs text-status-err">
          {error instanceof Error ? error.message : 'Failed to load related artifacts'}
        </p>
      )}
      {data && data.length === 0 && (
        <p className="text-xs text-fg-muted">
          No related artifacts yet — this may be the first of its kind.
        </p>
      )}
      {data && data.length > 0 && (
        <ul className="flex flex-col gap-3">
          {data.map((r) => (
            <RelatedItem key={r.artifact_path} r={r} onSelect={() => onSelect(r.artifact_path)} />
          ))}
        </ul>
      )}
    </aside>
  )
}

function RelatedItem({ r, onSelect }: { r: RelatedArtifact; onSelect: () => void }) {
  const filename = r.artifact_path.split('/').pop()?.replace(/\.md$/, '') ?? r.artifact_path
  const scorePct = Math.round(r.score * 100)

  return (
    <li>
      <button
        onClick={onSelect}
        className="w-full text-left flex flex-col gap-1.5 p-2 rounded-control border border-hairline hover:border-hairline-strong bg-surface-1 hover:bg-surface-2 transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      >
        <div className="flex items-baseline justify-between gap-2 min-w-0">
          <span className="text-sm text-fg font-medium truncate">{filename}</span>
          <span className="text-[10px] text-fg-subtle font-mono tabular-nums shrink-0">
            {scorePct}%
          </span>
        </div>
        {r.snippet && (
          <p className="text-[11px] text-fg-muted line-clamp-2 leading-relaxed">
            {r.snippet}
          </p>
        )}
        {r.shared_tags.length > 0 && (
          <p className="text-[10px] text-fg-subtle">
            Shares: <span className="text-fg-muted">{r.shared_tags.join(', ')}</span>
          </p>
        )}
      </button>
    </li>
  )
}
