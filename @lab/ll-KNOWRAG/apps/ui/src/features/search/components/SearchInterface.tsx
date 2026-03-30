import React, { useEffect, useState } from 'react';
import { knowledgeService } from '../../knowledge/services/knowledgeService';
import { Source, SearchResponse, ChunkSearchResult, PageSearchResult } from '../../knowledge/types';

export const SearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'chunk' | 'page'>('chunk');
  const [useHybrid, setUseHybrid] = useState(false);
  const [sourceFilter, setSourceFilter] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);

  useEffect(() => {
    knowledgeService.listSources().then(setSources).catch(() => {});
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await knowledgeService.queryKB(query, mode, useHybrid, sourceFilter || undefined);
      setResults(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '2rem', borderTop: '1px solid #eee', paddingTop: '2rem' }}>
      <h2>Query Knowledge Base</h2>
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask a question..."
          style={{ flex: 1, padding: '12px', fontSize: '16px', minWidth: '200px' }}
        />
        <select value={mode} onChange={e => setMode(e.target.value as any)} style={{ padding: '8px' }}>
          <option value="chunk">Chunk Mode</option>
          <option value="page">Page Mode</option>
        </select>
        <select value={sourceFilter} onChange={e => setSourceFilter(e.target.value)} style={{ padding: '8px' }}>
          <option value="">All Sources</option>
          {sources.map(s => (
            <option key={s.source_id} value={s.source_id}>
              {s.source_display_name || s.source_id}
            </option>
          ))}
        </select>
        <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '14px' }}>
          <input type="checkbox" checked={useHybrid} onChange={e => setUseHybrid(e.target.checked)} />
          Hybrid
        </label>
        <button type="submit" disabled={loading} style={{ padding: '8px 24px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results && (
        <div>
          <p style={{ color: '#666' }}>Found {results.total_results} results in {results.processing_time_ms.toFixed(1)}ms</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {results.mode === 'chunk' ? (
              (results.results as ChunkSearchResult[]).map((res, i) => (
                <div key={i} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px', fontSize: '14px', color: '#007bff' }}>{res.source_id} ({(res.similarity * 100).toFixed(1)}%)</div>
                  <div style={{ whiteSpace: 'pre-wrap' }}>{res.content}</div>
                </div>
              ))
            ) : (
              (results.results as PageSearchResult[]).map((res, i) => (
                <div key={i} style={{ padding: '1rem', border: '1px solid #ddd', borderRadius: '4px' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '18px' }}>{res.title || res.url}</div>
                  <div style={{ color: '#666', fontSize: '12px', marginBottom: '8px' }}>{res.source_id} | Max Sim: {(res.max_similarity * 100).toFixed(1)}%</div>
                  <div style={{ fontStyle: 'italic', backgroundColor: '#f9f9f9', padding: '8px' }}>
                    {res.chunks[0]?.content.substring(0, 300)}...
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
