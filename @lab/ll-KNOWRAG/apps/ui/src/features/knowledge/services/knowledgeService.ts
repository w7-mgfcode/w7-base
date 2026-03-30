import { Source, Page, SearchResponse, CrawlProgress, KBSummary, ChunkListResponse, SourceUpdateRequest, CrawlMode } from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8181';

export const knowledgeService = {
  async listSources(): Promise<Source[]> {
    const res = await fetch(`${API_BASE}/api/knowledge-items`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  async getSummary(): Promise<KBSummary> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/summary`);
    if (!res.ok) throw new Error('Failed to fetch summary');
    return res.json();
  },

  async updateSource(sourceId: string, data: SourceUpdateRequest): Promise<Source> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/${sourceId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update source');
    return res.json();
  },

  async refreshSource(sourceId: string): Promise<{ source_id: string; crawl_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/${sourceId}/refresh`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to refresh source');
    return res.json();
  },

  async startCrawl(
    url: string,
    sourceId?: string,
    maxDepth?: number,
    tags?: string[],
    mode?: CrawlMode,
    maxPages?: number,
  ): Promise<{ crawl_id: string }> {
    const body: Record<string, any> = { base_url: url, source_id: sourceId };
    if (maxDepth !== undefined) body.max_depth = maxDepth;
    if (mode) body.mode = mode;
    if (maxPages !== undefined) body.max_pages = maxPages;
    if (tags && tags.length > 0) {
      body.metadata = { tags };
    }
    const res = await fetch(`${API_BASE}/api/knowledge-items/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Failed to start crawl');
    return res.json();
  },

  async stopCrawl(progressId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/stop/${progressId}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to stop crawl');
  },

  async getCrawlProgress(crawlId: string): Promise<CrawlProgress> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/crawl-progress/${crawlId}`);
    if (!res.ok) throw new Error('Failed to fetch crawl progress');
    return res.json();
  },

  async uploadDocument(file: File, sourceId?: string, tags?: string): Promise<{ source_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) formData.append('source_id', sourceId);
    if (tags) formData.append('tags', tags);
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async queryKB(
    query: string,
    mode: 'chunk' | 'page' = 'chunk',
    useHybrid = false,
    filterSourceId?: string,
    useReranking = false,
    matchThreshold?: number,
    limit?: number,
  ): Promise<SearchResponse> {
    const body: Record<string, any> = { query, mode, use_hybrid: useHybrid, use_reranking: useReranking };
    if (filterSourceId) body.filter_source_id = filterSourceId;
    if (matchThreshold !== undefined) body.match_threshold = matchThreshold;
    if (limit !== undefined) body.limit = limit;
    const res = await fetch(`${API_BASE}/api/rag/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Failed to query KB');
    return res.json();
  },

  async listPages(sourceId?: string): Promise<Page[]> {
    const url = new URL(`${API_BASE}/api/pages`);
    if (sourceId) url.searchParams.append('source_id', sourceId);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch pages');
    return res.json();
  },

  async getPage(pageId: string): Promise<Page> {
    const res = await fetch(`${API_BASE}/api/pages/${pageId}`);
    if (!res.ok) throw new Error('Failed to fetch page content');
    return res.json();
  },

  async listChunks(sourceId: string, offset = 0, limit = 50): Promise<ChunkListResponse> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/${sourceId}/chunks?offset=${offset}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch chunks');
    return res.json();
  },

  async deleteSource(sourceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/${sourceId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete source');
  },
};
