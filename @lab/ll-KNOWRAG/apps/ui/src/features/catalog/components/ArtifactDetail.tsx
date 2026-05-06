import { useState } from 'react'
import { ArrowLeft, Check, Copy } from 'lucide-react'
import { useArtifact } from '../hooks/useCatalogQueries'
import { categoryFromPath } from '../types'
import { MarkdownView } from './MarkdownView'
import { RelatedPane } from './RelatedPane'
import { Button } from '../../../components/ui/Button'
import { Spinner } from '../../../components/ui/Spinner'

interface ArtifactDetailProps {
  path: string
  onBack: () => void
  onSelectRelated: (path: string) => void
}

export function ArtifactDetail({ path, onBack, onSelectRelated }: ArtifactDetailProps) {
  const { data, isLoading, isError, error } = useArtifact(path)
  const [copied, setCopied] = useState(false)
  const category = categoryFromPath(path)

  async function handleCopyMarkdown() {
    if (!data) return
    try {
      await navigator.clipboard.writeText(data.body)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      // best-effort
    }
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-fg-muted">
        <Spinner />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-md text-center">
          <p className="text-status-err mb-2">Failed to load artifact</p>
          <p className="text-sm text-fg-muted">
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <Button variant="secondary" size="sm" className="mt-4" onClick={onBack}>
            <ArrowLeft size={14} /> Back
          </Button>
        </div>
      </div>
    )
  }

  if (!data) return null

  const fm = data.frontmatter
  const filename = path.split('/').pop()?.replace(/\.md$/, '') ?? path
  const title = (fm['title'] as string) || filename
  const visibility = fm.visibility

  return (
    <div className="flex-1 flex min-h-0">
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center gap-3 px-6 h-14 border-b border-hairline bg-surface-0 shrink-0">
          <button
            onClick={onBack}
            className="text-fg-muted hover:text-fg cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded p-1"
            aria-label="Back to catalog"
          >
            <ArrowLeft size={18} />
          </button>
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2">
              <h2 className="text-base font-semibold text-fg truncate">{title}</h2>
              <span className="text-[10px] uppercase tracking-wide text-fg-subtle font-mono shrink-0">
                {category} · v{fm.version}
              </span>
            </div>
            <p className="text-xs text-fg-muted font-mono truncate">{path}</p>
          </div>
          <Button variant="secondary" size="sm" onClick={handleCopyMarkdown}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy markdown'}
          </Button>
        </header>

        <div className="border-b border-hairline bg-surface-1 px-6 py-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-fg-muted shrink-0">
          <span>
            owner <span className="text-fg font-mono">{fm.owner}</span>
          </span>
          <span>
            status <span className="text-fg font-mono">{fm.status}</span>
          </span>
          <span>
            visibility <span className="text-fg font-mono">{visibility}</span>
          </span>
          {fm.tags.length > 0 && (
            <span>
              tags <span className="text-fg font-mono">{fm.tags.join(', ')}</span>
            </span>
          )}
          {fm.updated_at && (
            <span>
              updated <span className="text-fg font-mono">{fm.updated_at}</span>
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <MarkdownView body={data.body} />
        </div>
      </div>
      <RelatedPane
        path={path}
        visibility={visibility === 'private' ? 'private' : 'public'}
        onSelect={onSelectRelated}
      />
    </div>
  )
}
