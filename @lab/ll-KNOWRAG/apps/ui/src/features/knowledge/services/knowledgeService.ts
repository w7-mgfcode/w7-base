import { Source, Page, SearchResponse, CrawlProgress } from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8181';

export const knowledgeService = {
  async listSources(): Promise<Source[]> {
    const res = await fetch(`${API_BASE}/api/knowledge-items`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  async startCrawl(url: string, sourceId?: string, maxDepth?: number, tags?: string): Promise<{ crawl_id: string }> {
    const body: Record<string, any> = { base_url: url, source_id: sourceId };
    if (maxDepth !== undefined) body.max_depth = maxDepth;
    if (tags) {
      body.metadata = { tags: tags.split(',').map(t => t.trim()).filter(Boolean) };
    }
    const res = await fetch(`${API_BASE}/api/knowledge-items/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Failed to start crawl');
    return res.json();
  },

  async getCrawlProgress(crawlId: string): Promise<CrawlProgress> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/crawl-progress/${crawlId}`);
    if (!res.ok) throw new Error('Failed to fetch crawl progress');
    return res.json();
  },

  async uploadDocument(file: File, sourceId?: string, tags?: string): Promise<{ source_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) {
      formData.append('source_id', sourceId);
    }
    if (tags) {
      formData.append('tags', tags);
    }

    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async queryKB(query: string, mode: 'chunk' | 'page' = 'chunk', useHybrid = false, filterSourceId?: string): Promise<SearchResponse> {
    const body: Record<string, any> = { query, mode, use_hybrid: useHybrid };
    if (filterSourceId) body.filter_source_id = filterSourceId;
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

  async deleteSource(sourceId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/knowledge-items/${sourceId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete source');
  }
};
