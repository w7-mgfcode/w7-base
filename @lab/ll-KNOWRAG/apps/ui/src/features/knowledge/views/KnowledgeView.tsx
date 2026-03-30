import React, { useEffect, useState } from 'react';
import { Source, Page } from '../types';
import { knowledgeService } from '../services/knowledgeService';
import { AddKnowledgeDialog } from '../components/AddKnowledgeDialog';
import { CrawlProgress } from '../components/CrawlProgress';
import { SearchInterface } from '../../search/components/SearchInterface';

export const KnowledgeView: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [activeCrawlId, setActiveCrawlId] = useState<string | null>(null);
  const [deletingSourceId, setDeletingSourceId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const loadSources = async () => {
    setLoading(true);
    try {
      const data = await knowledgeService.listSources();
      setSources(data);
      setLoadError(null);
    } catch (err) {
      console.error(err);
      setLoadError('Failed to load sources');
    } finally {
      setLoading(false);
    }
  };

  const loadPages = async (sourceId: string) => {
    try {
      const data = await knowledgeService.listPages(sourceId);
      setPages(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteSource = async (sourceId: string) => {
    const confirmed = window.confirm(`Delete source "${sourceId}"?`);
    if (!confirmed) {
      return;
    }

    setDeletingSourceId(sourceId);
    try {
      await knowledgeService.deleteSource(sourceId);
      if (selectedSource === sourceId) {
        setSelectedSource(null);
        setPages([]);
      }
      await loadSources();
    } catch (err) {
      console.error(err);
    } finally {
      setDeletingSourceId(null);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  useEffect(() => {
    if (selectedSource) {
      loadPages(selectedSource);
    } else {
      setPages([]);
    }
  }, [selectedSource]);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>KnowRAG Operator Console</h1>
        <button 
          onClick={() => setShowAdd(true)}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Add Knowledge
        </button>
      </header>

      {activeCrawlId && (
        <CrawlProgress
          crawlId={activeCrawlId}
          onComplete={() => {
            loadSources();
          }}
        />
      )}

      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Available Sources</h2>
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} style={{ padding: '6px 10px' }}>
            <option value="all">All Types</option>
            <option value="crawled">Crawled</option>
            <option value="uploaded">Uploaded</option>
          </select>
        </div>
        {loading ? <p>Loading sources...</p> : loadError ? (
          <div style={{ padding: '1rem', border: '1px solid #f0b3b3', borderRadius: '8px', backgroundColor: '#fff5f5' }}>
            <p style={{ marginTop: 0, color: '#b42318' }}>{loadError}</p>
            <button onClick={loadSources} style={{ padding: '8px 14px' }}>Retry</button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {sources.filter(s => {
              if (typeFilter === 'uploaded') return s.metadata?.upload === true;
              if (typeFilter === 'crawled') return !s.metadata?.upload;
              return true;
            }).map(s => (
              <div 
                key={s.source_id} 
                onClick={() => setSelectedSource(s.source_id)}
                style={{ 
                  padding: '1rem', 
                  border: '1px solid #ddd', 
                  borderRadius: '8px', 
                  cursor: 'pointer',
                  backgroundColor: selectedSource === s.source_id ? '#eef6ff' : 'white',
                  borderColor: selectedSource === s.source_id ? '#007bff' : '#ddd'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ fontWeight: 'bold' }}>{s.source_display_name || s.source_id}</div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSource(s.source_id);
                    }}
                    disabled={deletingSourceId === s.source_id}
                    style={{
                      border: '1px solid #f0b3b3',
                      backgroundColor: 'white',
                      color: '#b42318',
                      borderRadius: '4px',
                      padding: '4px 8px',
                      cursor: 'pointer',
                    }}
                  >
                    {deletingSourceId === s.source_id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
                <div style={{ fontSize: '12px', color: '#666', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.source_url}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {selectedSource && (
        <section style={{ marginTop: '2rem' }}>
          <h3>Pages in {selectedSource}</h3>
          <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid #eee', padding: '1rem' }}>
            {pages.length === 0 ? <p>No pages found.</p> : (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {pages.map(p => (
                  <li key={p.id} style={{ padding: '8px 0', borderBottom: '1px solid #f5f5f5', fontSize: '14px' }}>
                    {p.section_title || p.url}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      )}

      <SearchInterface />

      {showAdd && (
        <AddKnowledgeDialog
          onClose={() => setShowAdd(false)}
          onSuccess={(result) => {
            if (result?.crawlId) {
              setActiveCrawlId(result.crawlId);
            }
            loadSources();
          }}
        />
      )}
    </div>
  );
};
