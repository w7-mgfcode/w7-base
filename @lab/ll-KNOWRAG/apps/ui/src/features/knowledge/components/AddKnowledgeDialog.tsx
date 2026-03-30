import React, { useState } from 'react';
import { knowledgeService } from '../services/knowledgeService';

interface Props {
  onClose: () => void;
  onSuccess: (result?: { crawlId?: string; sourceId?: string }) => void;
}

export const AddKnowledgeDialog: React.FC<Props> = ({ onClose, onSuccess }) => {
  const [mode, setMode] = useState<'crawl' | 'upload'>('crawl');
  const [url, setUrl] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [tags, setTags] = useState('');
  const [maxDepth, setMaxDepth] = useState(1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCrawlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await knowledgeService.startCrawl(url, sourceId || undefined, maxDepth, tags || undefined);
      onSuccess({ crawlId: result.crawl_id, sourceId: sourceId || undefined });
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please choose a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await knowledgeService.uploadDocument(selectedFile, sourceId || undefined, tags || undefined);
      onSuccess({ sourceId: result.source_id });
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ backgroundColor: 'white', padding: '2rem', borderRadius: '8px', width: '400px' }}>
        <h2>Add Knowledge</h2>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <button
            type="button"
            onClick={() => setMode('crawl')}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: '6px',
              border: mode === 'crawl' ? '1px solid #007bff' : '1px solid #ddd',
              backgroundColor: mode === 'crawl' ? '#eef6ff' : 'white',
            }}
          >
            Crawl URL
          </button>
          <button
            type="button"
            onClick={() => setMode('upload')}
            style={{
              flex: 1,
              padding: '10px 12px',
              borderRadius: '6px',
              border: mode === 'upload' ? '1px solid #007bff' : '1px solid #ddd',
              backgroundColor: mode === 'upload' ? '#eef6ff' : 'white',
            }}
          >
            Upload File
          </button>
        </div>
        <form onSubmit={mode === 'crawl' ? handleCrawlSubmit : handleUploadSubmit}>
          {mode === 'crawl' && (
            <>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block' }}>Base URL</label>
                <input
                  type="url"
                  required
                  style={{ width: '100%', padding: '8px' }}
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  placeholder="https://docs.example.com"
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block' }}>Crawl Depth</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  style={{ width: '100%', padding: '8px' }}
                  value={maxDepth}
                  onChange={e => setMaxDepth(parseInt(e.target.value) || 1)}
                />
              </div>
            </>
          )}
          {mode === 'upload' && (
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block' }}>File</label>
              <input
                type="file"
                required
                onChange={e => setSelectedFile(e.target.files?.[0] ?? null)}
              />
            </div>
          )}
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block' }}>Source ID (Optional)</label>
            <input
              type="text"
              style={{ width: '100%', padding: '8px' }}
              value={sourceId}
              onChange={e => setSourceId(e.target.value)}
              placeholder="my-source-slug"
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block' }}>Tags (Optional)</label>
            <input
              type="text"
              style={{ width: '100%', padding: '8px' }}
              value={tags}
              onChange={e => setTags(e.target.value)}
              placeholder="tag1, tag2, tag3"
            />
          </div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
            <button type="button" onClick={onClose} disabled={loading}>Cancel</button>
            <button type="submit" disabled={loading} style={{ backgroundColor: '#007bff', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px' }}>
              {loading ? (mode === 'crawl' ? 'Starting...' : 'Uploading...') : (mode === 'crawl' ? 'Crawl URL' : 'Upload File')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
