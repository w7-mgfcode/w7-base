import { afterEach, describe, expect, it, vi } from 'vitest';
import { knowledgeService } from './knowledgeService';

describe('knowledgeService', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('lists sources from the knowledge endpoint', async () => {
    const payload = [{ source_id: 'docs', metadata: {}, created_at: '', updated_at: '' }];
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => payload,
      }),
    );

    const sources = await knowledgeService.listSources();

    expect(fetch).toHaveBeenCalledWith('http://localhost:8181/api/knowledge-items');
    expect(sources).toEqual(payload);
  });

  it('sends crawl requests with the expected payload', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ crawl_id: 'crawl-123' }),
      }),
    );

    const result = await knowledgeService.startCrawl('https://example.com', 'docs');

    expect(fetch).toHaveBeenCalledWith('http://localhost:8181/api/knowledge-items/crawl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base_url: 'https://example.com', source_id: 'docs' }),
    });
    expect(result).toEqual({ crawl_id: 'crawl-123' });
  });

  it('sends crawl requests with depth and tags', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ crawl_id: 'crawl-456' }),
      }),
    );

    await knowledgeService.startCrawl('https://example.com', 'docs', 3, 'api, reference');

    const call = (fetch as any).mock.calls[0];
    const body = JSON.parse(call[1].body);
    expect(body.max_depth).toBe(3);
    expect(body.metadata.tags).toEqual(['api', 'reference']);
  });

  it('sends query with source filter', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ query: 'test', mode: 'chunk', results: [], total_results: 0, processing_time_ms: 1 }),
      }),
    );

    await knowledgeService.queryKB('test', 'chunk', false, 'my-source');

    const call = (fetch as any).mock.calls[0];
    const body = JSON.parse(call[1].body);
    expect(body.filter_source_id).toBe('my-source');
  });
});
