import { useState, useCallback, useEffect } from 'react'
import { Source } from '../types'
import { useSources, useDeleteSource, useRefreshSource } from '../hooks/useKnowledgeQueries'
import { KBStatsBar } from '../components/KBStatsBar'
import { SourceList } from '../components/SourceList'
import { SourceDetail } from '../components/SourceDetail'
import { AddKnowledgeDialog } from '../components/AddKnowledgeDialog'
import { SearchInterface } from '../../search/components/SearchInterface'
import { Button } from '../../../components/ui/Button'
import { EmptyState } from '../../../components/ui/EmptyState'
import { Plus, Search as SearchIcon } from 'lucide-react'

export function KnowledgeView() {
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [searchMode, setSearchMode] = useState(false)
  const [activeCrawlIds, setActiveCrawlIds] = useState<string[]>([])
  const [deletingSourceId, setDeletingSourceId] = useState<string | null>(null)
  const [refreshError, setRefreshError] = useState<string | null>(null)

  const { data: sources = [], isLoading, isError } = useSources()

  // Ctrl+K to toggle search
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSearchMode((prev) => !prev)
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [])
  const deleteMutation = useDeleteSource()
  const refreshMutation = useRefreshSource()

  const handleDelete = useCallback(async (sourceId: string) => {
    if (!window.confirm(`Delete source "${sourceId}"?`)) return
    setDeletingSourceId(sourceId)
    try {
      await deleteMutation.mutateAsync(sourceId)
      if (selectedSource?.source_id === sourceId) setSelectedSource(null)
    } finally {
      setDeletingSourceId(null)
    }
  }, [deleteMutation, selectedSource])

  const handleRefresh = useCallback(async (sourceId: string) => {
    setRefreshError(null)
    try {
      const result = await refreshMutation.mutateAsync(sourceId)
      setActiveCrawlIds((prev) => [...prev, result.crawl_id])
    } catch (err: any) {
      setRefreshError(err.message || 'Refresh failed')
    }
  }, [refreshMutation])

  const handleCrawlComplete = useCallback((crawlId: string) => {
    setActiveCrawlIds((prev) => prev.filter((id) => id !== crawlId))
  }, [])

  const isEmpty = !isLoading && sources.length === 0

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-6 h-14 border-b border-border bg-bg-primary shrink-0">
        <h1 className="text-lg font-semibold tracking-tight">KnowRAG</h1>
        <div className="flex items-center gap-2">
          <Button onClick={() => setShowAdd(true)} size="sm">
            <Plus size={16} /> Add Knowledge
          </Button>
          <Button
            variant={searchMode ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setSearchMode(!searchMode)}
          >
            <SearchIcon size={16} /> Search
          </Button>
        </div>
      </header>

      {/* Stats Bar */}
      <KBStatsBar activeCrawlCount={activeCrawlIds.length} />

      {/* Refresh Error */}
      {refreshError && (
        <div className="px-6 py-2 bg-error/10 border-b border-error/20">
          <p className="text-sm text-error">Refresh failed: {refreshError}</p>
        </div>
      )}

      {/* Main Content */}
      {isError ? (
        <div className="flex-1 flex items-center justify-center">
          <EmptyState
            title="Failed to load sources"
            description="Could not connect to the API. Check that the backend is running."
          />
        </div>
      ) : isEmpty ? (
        <div className="flex-1 flex items-center justify-center">
          <EmptyState
            title="Your knowledge base is empty"
            description="Add your first source to start building your knowledge base. Crawl a website or upload a document."
            action={<Button onClick={() => setShowAdd(true)}>+ Add Knowledge</Button>}
          />
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          {/* Left Panel — Source List */}
          <div className="w-[380px] shrink-0 border-r border-border flex flex-col max-lg:w-full max-lg:hidden max-lg:data-[visible=true]:flex"
               data-visible={!selectedSource || undefined}>
            <SourceList
              sources={sources}
              isLoading={isLoading}
              selectedSourceId={selectedSource?.source_id ?? null}
              deletingSourceId={deletingSourceId}
              onSelect={setSelectedSource}
              onRefresh={handleRefresh}
              onDelete={handleDelete}
              onAddKnowledge={() => setShowAdd(true)}
            />
          </div>

          {/* Right Panel */}
          <div className="flex-1 overflow-hidden flex flex-col max-lg:w-full">
            {searchMode ? (
              <SearchInterface sources={sources} />
            ) : selectedSource ? (
              <SourceDetail
                source={selectedSource}
                activeCrawlIds={activeCrawlIds}
                onCrawlComplete={handleCrawlComplete}
                onRefresh={handleRefresh}
                onBack={() => setSelectedSource(null)}
              />
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <p className="text-text-tertiary text-sm">Select a source to view details</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Add Knowledge Dialog */}
      {showAdd && (
        <AddKnowledgeDialog
          onClose={() => setShowAdd(false)}
          onSuccess={(result) => {
            if (result?.crawlId) {
              setActiveCrawlIds((prev) => [...prev, result.crawlId!])
            }
          }}
        />
      )}
    </div>
  )
}
