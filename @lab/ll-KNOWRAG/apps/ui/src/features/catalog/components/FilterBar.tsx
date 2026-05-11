import { useMemo } from 'react'
import { X } from 'lucide-react'
import { Switch, ToggleGroup } from 'radix-ui'
import {
  ARTIFACT_CATEGORIES,
  ArtifactCategory,
  ArtifactSummary,
  Status,
} from '../types'

const STATUSES: Status[] = ['draft', 'review', 'published']

interface FilterBarProps {
  artifacts: ArtifactSummary[] // pre-filter universe (used for chip counts)
  category: ArtifactCategory | null
  tags: string[]
  status: Status[]
  owner: string | null
  vis: 'public' | 'private'
  hybrid: boolean
  rerank: boolean
  onCategoryChange: (category: ArtifactCategory | null) => void
  onTagsChange: (tags: string[]) => void
  onStatusChange: (status: Status[]) => void
  onOwnerChange: (owner: string | null) => void
  onVisChange: (vis: 'public' | 'private') => void
  onHybridChange: (hybrid: boolean) => void
  onRerankChange: (rerank: boolean) => void
  onClearAll: () => void
}

export function FilterBar({
  artifacts,
  category,
  tags,
  status,
  owner,
  vis,
  hybrid,
  rerank,
  onCategoryChange,
  onTagsChange,
  onStatusChange,
  onOwnerChange,
  onVisChange,
  onHybridChange,
  onRerankChange,
  onClearAll,
}: FilterBarProps) {
  const tagCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const a of artifacts) {
      for (const t of a.frontmatter.tags) counts.set(t, (counts.get(t) ?? 0) + 1)
    }
    return counts
  }, [artifacts])

  const owners = useMemo(() => {
    const counts = new Map<string, number>()
    for (const a of artifacts) {
      counts.set(a.frontmatter.owner, (counts.get(a.frontmatter.owner) ?? 0) + 1)
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1])
  }, [artifacts])

  const topTags = useMemo(
    () => [...tagCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12),
    [tagCounts],
  )

  const activeFilterCount =
    (category ? 1 : 0) +
    tags.length +
    status.length +
    (owner ? 1 : 0) +
    (vis !== 'public' ? 1 : 0) +
    (hybrid ? 1 : 0) +
    (rerank ? 1 : 0)

  function toggleTag(tag: string) {
    onTagsChange(
      tags.includes(tag) ? tags.filter((t) => t !== tag) : [...tags, tag],
    )
  }

  function toggleStatus(s: Status) {
    onStatusChange(
      status.includes(s) ? status.filter((x) => x !== s) : [...status, s],
    )
  }

  return (
    <div className="border-b border-hairline bg-surface-1">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3">
        <div className="flex items-center gap-1">
          <span className="text-[11px] text-fg-subtle uppercase tracking-wide mr-1">
            Type
          </span>
          <CategoryChip
            label="All"
            active={category === null}
            onClick={() => onCategoryChange(null)}
          />
          {ARTIFACT_CATEGORIES.map((c) => {
            const count = artifacts.filter((a) => a.path.startsWith(`${c}/`)).length
            return (
              <CategoryChip
                key={c}
                label={c}
                count={count}
                active={category === c}
                onClick={() => onCategoryChange(category === c ? null : c)}
              />
            )
          })}
        </div>

        <Divider />

        <div className="flex items-center gap-1">
          <span className="text-[11px] text-fg-subtle uppercase tracking-wide mr-1">
            Status
          </span>
          {STATUSES.map((s) => (
            <StatusChip
              key={s}
              label={s}
              active={status.includes(s)}
              onClick={() => toggleStatus(s)}
            />
          ))}
        </div>

        {owners.length > 0 && (
          <>
            <Divider />
            <div className="flex items-center gap-1">
              <span className="text-[11px] text-fg-subtle uppercase tracking-wide mr-1">
                Owner
              </span>
              <select
                value={owner ?? ''}
                onChange={(e) => onOwnerChange(e.target.value || null)}
                className="bg-surface-2 border border-hairline rounded-control px-2 py-1 text-xs text-fg focus-visible:border-accent focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface-0 focus-visible:outline-none"
              >
                <option value="">All</option>
                {owners.map(([name, count]) => (
                  <option key={name} value={name}>
                    {name} ({count})
                  </option>
                ))}
              </select>
            </div>
          </>
        )}

        {activeFilterCount > 0 && (
          <button
            onClick={onClearAll}
            className="text-xs text-fg-muted hover:text-fg cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded px-1"
          >
            Clear ({activeFilterCount})
          </button>
        )}

        <div
          className="ml-auto flex items-center gap-2 max-w-full"
          aria-label="Search scope controls"
        >
          <span className="text-[11px] text-fg-subtle uppercase tracking-wide mr-1">
            Scope
          </span>
          <ToggleGroup.Root
            type="single"
            value={vis}
            onValueChange={(v) => {
              if (v === 'public' || v === 'private') onVisChange(v)
            }}
            className="flex items-center"
            aria-label="Visibility"
          >
            <ToggleGroup.Item
              value="public"
              className="text-xs px-2 py-1 rounded-l-control border border-hairline text-fg-muted bg-surface-2 hover:text-fg cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent data-[state=on]:bg-accent/15 data-[state=on]:text-accent data-[state=on]:border-accent/40"
            >
              public
            </ToggleGroup.Item>
            <ToggleGroup.Item
              value="private"
              className="text-xs px-2 py-1 rounded-r-control border border-l-0 border-hairline text-fg-muted bg-surface-2 hover:text-fg cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent data-[state=on]:bg-accent/15 data-[state=on]:text-accent data-[state=on]:border-accent/40"
            >
              private
            </ToggleGroup.Item>
          </ToggleGroup.Root>
          <ScopeSwitch
            label="hybrid"
            checked={hybrid}
            onCheckedChange={onHybridChange}
          />
          <ScopeSwitch
            label="rerank"
            checked={rerank}
            onCheckedChange={onRerankChange}
          />
        </div>
      </div>

      {topTags.length > 0 && (
        <div className="flex flex-wrap items-center gap-1 px-4 pb-3">
          <span className="text-[11px] text-fg-subtle uppercase tracking-wide mr-1">
            Tags
          </span>
          {topTags.map(([tag, count]) => {
            const active = tags.includes(tag)
            return (
              <button
                key={tag}
                onClick={() => toggleTag(tag)}
                className={`text-[11px] px-2 py-0.5 rounded-full border transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                  active
                    ? 'bg-accent/15 text-accent border-accent/40'
                    : 'bg-surface-2 text-fg-muted border-hairline hover:border-hairline-strong hover:text-fg'
                }`}
              >
                {active && <span className="mr-1">✓</span>}
                {tag}
                <span className="ml-1 text-fg-subtle font-mono tabular-nums">
                  {count}
                </span>
                {active && (
                  <X size={10} className="inline ml-1 align-middle" aria-hidden />
                )}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

function Divider() {
  return <span className="w-px h-5 bg-hairline" aria-hidden />
}

function ScopeSwitch({
  label,
  checked,
  onCheckedChange,
}: {
  label: string
  checked: boolean
  onCheckedChange: (checked: boolean) => void
}) {
  return (
    <label className="flex items-center gap-1.5 text-xs text-fg-muted cursor-pointer select-none">
      <Switch.Root
        checked={checked}
        onCheckedChange={onCheckedChange}
        aria-label={label}
        className="relative inline-flex h-4 w-7 shrink-0 items-center rounded-full border border-hairline bg-surface-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent data-[state=checked]:border-accent/40 data-[state=checked]:bg-accent/15 cursor-pointer"
      >
        <Switch.Thumb className="block h-3 w-3 translate-x-0.5 rounded-full bg-fg-muted transition-transform data-[state=checked]:translate-x-3.5 data-[state=checked]:bg-accent" />
      </Switch.Root>
      <span className={checked ? 'text-accent' : undefined}>{label}</span>
    </label>
  )
}

function CategoryChip({
  label,
  count,
  active,
  onClick,
}: {
  label: string
  count?: number
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`text-xs px-2 py-1 rounded-control border font-medium transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        active
          ? 'bg-accent text-white border-accent'
          : 'bg-surface-2 text-fg-muted border-hairline hover:border-hairline-strong hover:text-fg'
      }`}
    >
      {label}
      {count !== undefined && (
        <span className="ml-1 font-mono tabular-nums opacity-80">{count}</span>
      )}
    </button>
  )
}

function StatusChip({
  label,
  active,
  onClick,
}: {
  label: Status
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`text-xs px-2 py-1 rounded-control border transition-colors cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        active
          ? 'bg-accent/15 text-accent border-accent/40'
          : 'bg-surface-2 text-fg-muted border-hairline hover:border-hairline-strong hover:text-fg'
      }`}
    >
      {label}
    </button>
  )
}
