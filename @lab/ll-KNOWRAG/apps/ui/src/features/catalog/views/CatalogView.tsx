import { useEffect, useMemo, useState } from 'react'
import {
  parseAsBoolean,
  parseAsString,
  parseAsArrayOf,
  parseAsStringLiteral,
  useQueryState,
} from 'nuqs'
import { Command as CommandIcon, Search as SearchIcon } from 'lucide-react'
import { ArtifactCard } from '../components/ArtifactCard'
import { FilterBar } from '../components/FilterBar'
import { ArtifactDetail } from '../components/ArtifactDetail'
import { SearchPalette } from '../components/SearchPalette'
import { useArtifacts } from '../hooks/useCatalogQueries'
import {
  ARTIFACT_CATEGORIES,
  ArtifactCategory,
  ArtifactSummary,
  Status,
  STATUS_VALUES,
  categoryFromPath,
} from '../types'
import { Button } from '../../../components/ui/Button'
import { EmptyState } from '../../../components/ui/EmptyState'
import { Spinner } from '../../../components/ui/Spinner'

const CATEGORY_VALUES = ARTIFACT_CATEGORIES

export function CatalogView() {
  // URL-synced filter state via nuqs.
  const [category, setCategory] = useQueryState(
    'cat',
    parseAsStringLiteral(CATEGORY_VALUES).withDefault('' as ArtifactCategory),
  )
  const [tags, setTags] = useQueryState(
    'tags',
    parseAsArrayOf(parseAsString).withDefault([]),
  )
  const [statusList, setStatusList] = useQueryState(
    'status',
    parseAsArrayOf(parseAsStringLiteral(STATUS_VALUES)).withDefault([]),
  )
  const [owner, setOwner] = useQueryState('owner', parseAsString)
  const [vis, setVis] = useQueryState(
    'vis',
    parseAsStringLiteral(['public', 'private'] as const).withDefault('public'),
  )
  const [hybrid, setHybrid] = useQueryState(
    'hybrid',
    parseAsBoolean.withDefault(false),
  )
  const [rerank, setRerank] = useQueryState(
    'rerank',
    parseAsBoolean.withDefault(false),
  )
  const [selectedPath, setSelectedPath] = useQueryState('a', parseAsString)
  const [paletteOpen, setPaletteOpen] = useState(false)

  const cat: ArtifactCategory | null =
    category && (CATEGORY_VALUES as readonly string[]).includes(category)
      ? (category as ArtifactCategory)
      : null

  const { data: allArtifacts = [], isLoading, isError, error } = useArtifacts(cat ?? undefined)

  // Ctrl+K / Cmd+K to open search.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setPaletteOpen(true)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const filtered = useMemo(() => {
    return allArtifacts.filter((a) => {
      if (tags.length && !tags.some((t) => a.frontmatter.tags.includes(t))) return false
      if (statusList.length && !statusList.includes(a.frontmatter.status)) return false
      if (owner && a.frontmatter.owner !== owner) return false
      return true
    })
  }, [allArtifacts, tags, statusList, owner])

  function clearAll() {
    setCategory('' as ArtifactCategory)
    setTags([])
    setStatusList([])
    setOwner(null)
    setVis('public')
    setHybrid(false)
    setRerank(false)
  }

  function handleSelect(path: string) {
    setSelectedPath(path)
  }

  if (selectedPath) {
    return (
      <div className="flex flex-col h-full">
        <ArtifactDetail
          path={selectedPath}
          onBack={() => setSelectedPath(null)}
          onSelectRelated={(p) => setSelectedPath(p)}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <FilterBar
        artifacts={allArtifacts}
        category={cat}
        tags={tags}
        status={statusList}
        owner={owner}
        vis={vis}
        hybrid={hybrid}
        rerank={rerank}
        onCategoryChange={(c) => setCategory((c ?? '') as ArtifactCategory)}
        onTagsChange={(ts) => setTags(ts)}
        onStatusChange={(ss) => setStatusList(ss as Status[])}
        onOwnerChange={(o) => setOwner(o)}
        onVisChange={(v) => setVis(v)}
        onHybridChange={(b) => setHybrid(b)}
        onRerankChange={(b) => setRerank(b)}
        onClearAll={clearAll}
      />

      <main className="flex-1 overflow-y-auto p-4 @container">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs text-fg-muted font-mono">
            {filtered.length}
            {filtered.length !== allArtifacts.length && (
              <> / {allArtifacts.length}</>
            )}{' '}
            artifacts
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPaletteOpen(true)}
            aria-label="Open search palette"
          >
            <SearchIcon size={14} />
            Search
            <span className="ml-1 inline-flex items-center gap-0.5 text-[10px] text-fg-subtle font-mono border border-hairline rounded px-1 py-0.5">
              <CommandIcon size={10} />K
            </span>
          </Button>
        </div>
        {isLoading && (
          <div className="flex items-center justify-center pt-20 text-fg-muted">
            <Spinner />
          </div>
        )}
        {isError && (
          <EmptyState
            title="Failed to load catalog"
            description={error instanceof Error ? error.message : 'Unknown error'}
          />
        )}
        {!isLoading && !isError && filtered.length === 0 && (
          <EmptyState
            title="No artifacts match these filters"
            description="Clear filters or add knowledge to the Gitea repo."
          />
        )}
        {!isLoading && !isError && filtered.length > 0 && (
          <CardGrid artifacts={filtered} onSelect={handleSelect} />
        )}
      </main>

      <SearchPalette
        open={paletteOpen}
        onOpenChange={setPaletteOpen}
        artifacts={allArtifacts}
        vis={vis}
        hybrid={hybrid}
        rerank={rerank}
        onSelect={handleSelect}
      />
    </div>
  )
}

function CardGrid({
  artifacts,
  onSelect,
}: {
  artifacts: ArtifactSummary[]
  onSelect: (path: string) => void
}) {
  // Container-query grid: 2-col baseline, 3 at md (~768px), 4 at xl (~1280px),
  // 5 at 2xl (~1600px). Tied to the parent's container, not viewport.
  return (
    <div className="grid gap-3 grid-cols-2 @md:grid-cols-3 @xl:grid-cols-4 @[1600px]:grid-cols-5">
      {artifacts.map((a) => {
        const _category = categoryFromPath(a.path)
        void _category
        return (
          <ArtifactCard
            key={a.path}
            artifact={a}
            onClick={() => onSelect(a.path)}
          />
        )
      })}
    </div>
  )
}
