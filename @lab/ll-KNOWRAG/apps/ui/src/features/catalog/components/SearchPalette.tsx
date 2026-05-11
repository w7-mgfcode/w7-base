import { useEffect, useMemo, useState } from 'react'
import { Command } from 'cmdk'
import { Dialog as RadixDialog, VisuallyHidden } from 'radix-ui'
import { Search } from 'lucide-react'
import { ArtifactSummary, categoryFromPath } from '../types'
import { useArtifactSearch } from '../hooks/useCatalogQueries'

interface SearchPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  artifacts: ArtifactSummary[]
  vis: 'public' | 'private'
  hybrid: boolean
  rerank: boolean
  onSelect: (path: string) => void
}

export function SearchPalette({
  open,
  onOpenChange,
  artifacts,
  vis,
  hybrid,
  rerank,
  onSelect,
}: SearchPaletteProps) {
  const [input, setInput] = useState('')
  const [debounced, setDebounced] = useState('')

  useEffect(() => {
    const id = window.setTimeout(() => setDebounced(input.trim()), 80)
    return () => window.clearTimeout(id)
  }, [input])

  // Reset on close.
  useEffect(() => {
    if (!open) setInput('')
  }, [open])

  const activeModifiers = [
    vis === 'private' ? 'private' : null,
    hybrid ? 'hybrid' : null,
    rerank ? 'rerank' : null,
  ].filter((m): m is string => m !== null)

  const localMatches = useMemo(() => {
    if (!input.trim()) return artifacts.slice(0, 8)
    const needle = input.toLowerCase()
    return artifacts
      .filter((a) => {
        const filename = a.path.split('/').pop()?.toLowerCase() ?? ''
        const title = String(a.frontmatter['title'] ?? '').toLowerCase()
        const tags = a.frontmatter.tags.join(' ').toLowerCase()
        return (
          filename.includes(needle) ||
          a.path.toLowerCase().includes(needle) ||
          title.includes(needle) ||
          tags.includes(needle)
        )
      })
      .slice(0, 12)
  }, [artifacts, input])

  const semanticArgs = debounced
    ? {
        query: debounced,
        topK: 8,
        visibility: vis,
        useHybrid: hybrid,
        useRerank: rerank,
      }
    : null
  const semantic = useArtifactSearch(semanticArgs)

  const grouped = useMemo(() => groupByCategory(localMatches), [localMatches])
  const semanticPages = (semantic.data?.pages ?? []).filter(
    (p) => !localMatches.some((a) => a.path === p.artifact_path),
  )

  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
      <RadixDialog.Portal>
        <RadixDialog.Overlay className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm data-[state=open]:animate-in data-[state=open]:fade-in" />
        <RadixDialog.Content
          className="fixed left-1/2 top-[20%] z-50 -translate-x-1/2 w-full max-w-xl mx-4 bg-surface-1 border border-hairline rounded-modal shadow-2xl overflow-hidden focus:outline-none data-[state=open]:animate-in data-[state=open]:zoom-in-95"
          aria-label="Search KB artifacts"
        >
          <VisuallyHidden.Root>
            <RadixDialog.Title>Search KB artifacts</RadixDialog.Title>
            <RadixDialog.Description>
              Find artifacts by title, path, tag, or semantic query. Use arrow
              keys to navigate, Enter to open, Esc to close.
            </RadixDialog.Description>
          </VisuallyHidden.Root>
          <Command shouldFilter={false} className="flex flex-col">
            <div className="flex items-center gap-2 px-4 h-12 border-b border-hairline">
              <Search size={16} className="text-fg-subtle" />
              <Command.Input
                value={input}
                onValueChange={setInput}
                placeholder="Search artifacts by title, path, tag, or semantic query…"
                autoFocus
                className="flex-1 bg-transparent text-sm text-fg placeholder:text-fg-subtle focus:outline-none"
              />
              {semantic.isFetching && (
                <span className="text-[10px] text-fg-subtle font-mono">…</span>
              )}
            </div>
            {activeModifiers.length > 0 && (
              <div
                className="px-4 py-1 border-b border-hairline text-[10px] text-fg-muted font-mono"
                aria-label="Active search scope"
              >
                Scope: {activeModifiers.join(' · ')}
              </div>
            )}
            <Command.List className="max-h-[60vh] overflow-y-auto py-2">
              <Command.Empty className="px-4 py-6 text-sm text-fg-muted">
                No results.
              </Command.Empty>

              {grouped.map(([category, items]) => (
                <Command.Group
                  key={category}
                  heading={
                    <span className="px-3 py-1 text-[10px] uppercase tracking-wide text-fg-subtle">
                      {category}
                    </span>
                  }
                >
                  {items.map((a) => (
                    <ArtifactRow
                      key={a.path}
                      summary={a}
                      query={input}
                      onSelect={() => {
                        onSelect(a.path)
                        onOpenChange(false)
                      }}
                    />
                  ))}
                </Command.Group>
              ))}

              {semanticPages.length > 0 && (
                <Command.Group
                  heading={
                    <span className="px-3 py-1 text-[10px] uppercase tracking-wide text-fg-subtle">
                      semantic
                    </span>
                  }
                >
                  {semanticPages.map((p) => (
                    <Command.Item
                      key={p.artifact_path}
                      value={`semantic:${p.artifact_path}`}
                      onSelect={() => {
                        onSelect(p.artifact_path)
                        onOpenChange(false)
                      }}
                      className="px-3 py-2 text-sm cursor-pointer data-[selected=true]:bg-surface-2 data-[selected=true]:text-fg flex items-center justify-between gap-3"
                    >
                      <span className="truncate text-fg">
                        {p.artifact_path.split('/').pop()?.replace(/\.md$/, '')}
                      </span>
                      <span className="text-[10px] text-fg-subtle font-mono tabular-nums">
                        {Math.round(p.top_score * 100)}%
                      </span>
                    </Command.Item>
                  ))}
                </Command.Group>
              )}
            </Command.List>
            <div className="border-t border-hairline px-3 py-2 text-[10px] text-fg-subtle font-mono flex items-center justify-between">
              <span>↑↓ navigate · Enter open · Esc close</span>
              <span>{artifacts.length} artifacts</span>
            </div>
          </Command>
        </RadixDialog.Content>
      </RadixDialog.Portal>
    </RadixDialog.Root>
  )
}

function ArtifactRow({
  summary,
  query,
  onSelect,
}: {
  summary: ArtifactSummary
  query: string
  onSelect: () => void
}) {
  const filename = summary.path.split('/').pop()?.replace(/\.md$/, '') ?? summary.path
  const title = (summary.frontmatter['title'] as string) || filename

  return (
    <Command.Item
      value={summary.path}
      onSelect={onSelect}
      className="px-3 py-2 text-sm cursor-pointer data-[selected=true]:bg-surface-2 data-[selected=true]:text-fg flex flex-col gap-0.5"
    >
      <div className="flex items-baseline justify-between gap-3 min-w-0">
        <span className="text-fg truncate">{highlight(title, query)}</span>
        <span className="text-[10px] text-fg-subtle font-mono shrink-0">
          {summary.frontmatter.status}
        </span>
      </div>
      <span className="text-[11px] text-fg-muted font-mono truncate">
        {summary.path}
      </span>
    </Command.Item>
  )
}

function highlight(text: string, query: string) {
  if (!query) return text
  const idx = text.toLowerCase().indexOf(query.toLowerCase())
  if (idx < 0) return text
  return (
    <>
      {text.slice(0, idx)}
      <mark className="bg-accent/20 text-fg rounded px-0.5">
        {text.slice(idx, idx + query.length)}
      </mark>
      {text.slice(idx + query.length)}
    </>
  )
}

function groupByCategory(
  items: ArtifactSummary[],
): Array<[string, ArtifactSummary[]]> {
  const groups = new Map<string, ArtifactSummary[]>()
  for (const a of items) {
    const cat = categoryFromPath(a.path) ?? 'other'
    const arr = groups.get(cat) ?? []
    arr.push(a)
    groups.set(cat, arr)
  }
  return [...groups.entries()]
}
