import { ArtifactSummary, categoryFromPath } from '../types'
import { Card } from '../../../components/ui/Card'

interface ArtifactCardProps {
  artifact: ArtifactSummary
  selected?: boolean
  onClick?: () => void
}

const STATUS_TONE: Record<string, string> = {
  published: 'bg-accent/10 text-accent border-accent/30',
  review: 'bg-status-warn/10 text-status-warn border-status-warn/30',
  draft: 'bg-surface-2 text-fg-muted border-hairline',
}

export function ArtifactCard({ artifact, selected, onClick }: ArtifactCardProps) {
  const fm = artifact.frontmatter
  const category = categoryFromPath(artifact.path)
  const filename = artifact.path.split('/').pop()?.replace(/\.md$/, '') ?? artifact.path
  const title = (fm['title'] as string) || filename
  const description = (fm['description'] as string) || (fm['summary'] as string) || ''
  const visibleTags = fm.tags.slice(0, 2)
  const moreTagCount = Math.max(0, fm.tags.length - visibleTags.length)
  const ownerInitials = fm.owner
    .split(/[\s_-]+/)
    .map((p) => p[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase() || fm.owner.slice(0, 2).toUpperCase()
  const statusClass = STATUS_TONE[fm.status] ?? STATUS_TONE.draft

  return (
    <Card
      selected={selected}
      onClick={onClick}
      className="cursor-pointer h-[148px] flex flex-col gap-2 group"
    >
      <div className="flex items-start justify-between gap-2 min-w-0">
        <h3 className="text-sm font-semibold text-fg truncate flex-1" title={title}>
          {title}
        </h3>
        <span
          className={`shrink-0 text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded-full border font-medium ${statusClass}`}
        >
          {fm.status}
        </span>
      </div>

      {description && (
        <p className="text-xs text-fg-muted line-clamp-2 leading-relaxed">{description}</p>
      )}

      <div className="flex items-center gap-1 flex-wrap">
        {visibleTags.map((tag) => (
          <span
            key={tag}
            className="text-[11px] px-1.5 py-0.5 rounded-full bg-surface-2 text-fg-muted border border-hairline"
          >
            {tag}
          </span>
        ))}
        {moreTagCount > 0 && (
          <span className="text-[11px] text-fg-subtle">+{moreTagCount}</span>
        )}
      </div>

      <div className="mt-auto flex items-center justify-between gap-2 pt-2 border-t border-hairline text-[11px] text-fg-subtle">
        <div className="flex items-center gap-2 min-w-0">
          <span
            className="size-5 rounded-full bg-surface-2 border border-hairline flex items-center justify-center text-[9px] text-fg-muted shrink-0"
            title={fm.owner}
          >
            {ownerInitials}
          </span>
          <span className="truncate font-mono">{category ?? '·'}</span>
        </div>
        <span className="font-mono tabular-nums shrink-0">v{fm.version}</span>
      </div>
    </Card>
  )
}
