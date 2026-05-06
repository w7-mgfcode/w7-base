import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { knowledgeService } from '../services/knowledgeService'
import { SourceUpdateRequest, CrawlMode } from '../types'

const KEYS = {
  sources: ['sources'] as const,
  summary: ['kb-summary'] as const,
  pages: (sourceId: string) => ['pages', sourceId] as const,
  page: (pageId: string) => ['page', pageId] as const,
  chunks: (sourceId: string, offset: number, limit: number) => ['chunks', sourceId, offset, limit] as const,
  crawlProgress: (crawlId: string) => ['crawl-progress', crawlId] as const,
}

export function useSources() {
  return useQuery({
    queryKey: KEYS.sources,
    queryFn: () => knowledgeService.listSources(),
  })
}

export function useKBSummary() {
  return useQuery({
    queryKey: KEYS.summary,
    queryFn: () => knowledgeService.getSummary(),
    staleTime: 30_000,
  })
}

export function usePages(sourceId: string | undefined) {
  return useQuery({
    queryKey: KEYS.pages(sourceId!),
    queryFn: () => knowledgeService.listPages(sourceId),
    enabled: !!sourceId,
  })
}

export function usePage(pageId: string | undefined) {
  return useQuery({
    queryKey: KEYS.page(pageId!),
    queryFn: () => knowledgeService.getPage(pageId!),
    enabled: !!pageId,
  })
}

export function useChunks(sourceId: string | undefined, offset = 0, limit = 50) {
  return useQuery({
    queryKey: KEYS.chunks(sourceId!, offset, limit),
    queryFn: () => knowledgeService.listChunks(sourceId!, offset, limit),
    enabled: !!sourceId,
  })
}

export function useCrawlProgress(crawlId: string | null) {
  return useQuery({
    queryKey: KEYS.crawlProgress(crawlId!),
    queryFn: () => knowledgeService.getCrawlProgress(crawlId!),
    enabled: !!crawlId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'completed' || status === 'failed' || status === 'cancelled') return false
      return 2000
    },
  })
}

export function useUpdateSource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ sourceId, data }: { sourceId: string; data: SourceUpdateRequest }) =>
      knowledgeService.updateSource(sourceId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.sources })
      qc.invalidateQueries({ queryKey: KEYS.summary })
    },
  })
}

export function useDeleteSource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sourceId: string) => knowledgeService.deleteSource(sourceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.sources })
      qc.invalidateQueries({ queryKey: KEYS.summary })
    },
  })
}

export function useRefreshSource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sourceId: string) => knowledgeService.refreshSource(sourceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.sources })
      qc.invalidateQueries({ queryKey: KEYS.summary })
    },
  })
}

export function useUploadDocument() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ file, tags }: { file: File; tags?: string }) =>
      knowledgeService.uploadDocument(file, undefined, tags || undefined),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.sources })
      qc.invalidateQueries({ queryKey: KEYS.summary })
    },
  })
}

export function useStartCrawl() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (params: {
      url: string
      sourceId?: string
      maxDepth?: number
      tags?: string[]
      mode?: CrawlMode
      maxPages?: number
    }) =>
      knowledgeService.startCrawl(params.url, params.sourceId, params.maxDepth, params.tags, params.mode, params.maxPages),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: KEYS.sources })
    },
  })
}

export function useStopCrawl() {
  return useMutation({
    mutationFn: (progressId: string) => knowledgeService.stopCrawl(progressId),
  })
}

export function useSearchMutation() {
  return useMutation({
    mutationFn: (params: {
      query: string
      mode?: 'chunk' | 'page'
      useHybrid?: boolean
      filterSourceId?: string
      useReranking?: boolean
      matchThreshold?: number
      limit?: number
    }) =>
      knowledgeService.queryKB(
        params.query,
        params.mode,
        params.useHybrid,
        params.filterSourceId,
        params.useReranking,
        params.matchThreshold,
        params.limit,
      ),
  })
}
