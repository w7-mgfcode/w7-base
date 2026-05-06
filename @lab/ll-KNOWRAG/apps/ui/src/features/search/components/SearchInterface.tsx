import { useState, useMemo } from 'react'
import { Source, SearchResponse, ChunkSearchResult, PageSearchResult } from '../../knowledge/types'
import { useSearchMutation } from '../../knowledge/hooks/useKnowledgeQueries'
import { Input } from '../../../components/ui/Input'
import { Select } from '../../../components/ui/Select'
import { Button } from '../../../components/ui/Button'
import { Slider } from '../../../components/ui/Slider'
import { Spinner } from '../../../components/ui/Spinner'
import { Card } from '../../../components/ui/Card'
import { Badge } from '../../../components/ui/Badge'
import { EmptyState } from '../../../components/ui/EmptyState'
import { Search, ExternalLink } from 'lucide-react'

interface SearchInterfaceProps {
  sources?: Source[]
}

function similarityColor(sim: number): string {
  if (sim >= 0.8) return 'text-accent'
  if (sim >= 0.5) return 'text-status-warn'
  return 'text-status-err'
}

export function SearchInterface({ sources = [] }: SearchInterfaceProps) {
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<'chunk' | 'page'>('chunk')
  const [useHybrid, setUseHybrid] = useState(false)
  const [useReranking, setUseReranking] = useState(false)
  const [sourceFilter, setSourceFilter] = useState('')
  const [threshold, setThreshold] = useState(0.0)
  const [limit, setLimit] = useState(10)

  const duplicateNames = useMemo(() => {
    const counts = new Map<string, number>()
    for (const s of sources) {
      const name = s.source_display_name || s.source_id
      counts.set(name, (counts.get(name) || 0) + 1)
    }
    return new Set([...counts.entries()].filter(([, c]) => c > 1).map(([n]) => n))
  }, [sources])

  const searchMutation = useSearchMutation()
  const results: SearchResponse | undefined = searchMutation.data

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!query.trim()) return
    searchMutation.mutate({
      query,
      mode,
      useHybrid,
      filterSourceId: sourceFilter || undefined,
      useReranking,
      matchThreshold: threshold > 0 ? threshold : undefined,
      limit,
    })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Search input */}
      <div className="p-4 border-b border-hairline">
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-fg-subtle" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search your knowledge base..."
            className="pl-9 text-base"
          />
        </div>
      </div>

      {/* Controls */}
      <div className="px-4 py-3 border-b border-hairline space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <Select value={mode} onChange={(e) => setMode(e.target.value as 'chunk' | 'page')} className="w-28 text-xs">
            <option value="chunk">Chunk</option>
            <option value="page">Page</option>
          </Select>
          <Select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)} className="w-40 text-xs">
            <option value="">All Sources</option>
            {sources.map((s) => {
              const label = s.source_display_name || s.source_id
              return (
                <option key={s.source_id} value={s.source_id}>
                  {duplicateNames.has(label) ? `${label} (${s.source_id})` : label}
                </option>
              )
            })}
          </Select>
          <label className="flex items-center gap-1.5 text-xs text-fg-muted cursor-pointer">
            <input type="checkbox" checked={useHybrid} onChange={(e) => setUseHybrid(e.target.checked)}
              className="accent-accent" />
            Hybrid
          </label>
          <label className="flex items-center gap-1.5 text-xs text-fg-muted cursor-pointer">
            <input type="checkbox" checked={useReranking} onChange={(e) => setUseReranking(e.target.checked)}
              className="accent-accent" />
            Rerank
          </label>
          <Button onClick={() => handleSearch()} disabled={searchMutation.isPending || !query.trim()} size="sm">
            {searchMutation.isPending ? <Spinner size={14} /> : 'Go'}
          </Button>
        </div>
        <div className="flex items-center gap-4">
          <Slider
            label="Threshold"
            min={0}
            max={1}
            step={0.05}
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            displayValue={threshold.toFixed(2)}
            className="flex-1"
          />
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-fg-muted">Limit</span>
            <Select value={limit} onChange={(e) => setLimit(Number(e.target.value))} className="w-16 text-xs">
              {[5, 10, 25, 50].map((n) => <option key={n} value={n}>{n}</option>)}
            </Select>
          </div>
        </div>
      </div>

      {/* Search Error */}
      {searchMutation.isError && (
        <div className="px-4 pt-3">
          <p className="text-sm text-status-err">Search failed. Check that the API is running and try again.</p>
        </div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-4">
        {results && (
          <>
            <p className="text-xs text-fg-muted mb-3">
              {results.total_results} result{results.total_results !== 1 ? 's' : ''} in {results.processing_time_ms.toFixed(0)}ms
              {results.reranking_applied && <Badge variant="accent" className="ml-2">reranked</Badge>}
            </p>
            <div className="space-y-2">
              {results.mode === 'chunk' ? (
                (results.results as ChunkSearchResult[]).map((r, i) => (
                  <Card key={i} className="p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm font-bold ${similarityColor(r.similarity)}`}>
                        {(r.similarity * 100).toFixed(1)}%
                      </span>
                      <span className="text-xs text-fg-muted">{r.source_id}</span>
                    </div>
                    <p className="text-sm text-fg line-clamp-3 mb-1">{r.content}</p>
                    {r.contextual_content && (
                      <p className="text-xs text-fg-subtle line-clamp-1">{r.contextual_content}</p>
                    )}
                  </Card>
                ))
              ) : (
                (results.results as PageSearchResult[]).map((r, i) => (
                  <Card key={i} className="p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm font-bold ${similarityColor(r.max_similarity)}`}>
                        {(r.max_similarity * 100).toFixed(1)}%
                      </span>
                      <span className="text-xs text-fg-muted">{r.chunk_count} chunks</span>
                    </div>
                    <p className="text-sm font-medium mb-0.5">{r.title || r.url}</p>
                    <p className="text-xs text-fg-muted font-mono mb-2">{r.url}</p>
                    {r.chunks[0] && (
                      <p className="text-xs text-fg-subtle line-clamp-2">{r.chunks[0].content}</p>
                    )}
                  </Card>
                ))
              )}
            </div>
          </>
        )}
        {!results && !searchMutation.isPending && (
          <EmptyState
            icon={<Search size={40} />}
            title="Search your knowledge base"
            description="Enter a query above to find relevant content across all your sources."
          />
        )}
      </div>
    </div>
  )
}
