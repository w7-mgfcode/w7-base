import React, { useEffect, useRef, useState } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { CrawlProgress as CrawlProgressModel } from '../types';

interface Props {
  crawlId: string;
  onComplete?: () => void;
}

export const CrawlProgress: React.FC<Props> = ({ crawlId, onComplete }) => {
  const [progress, setProgress] = useState<CrawlProgressModel | null>(null);
  const [error, setError] = useState<string | null>(null);
  const notifiedCompleteRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const next = await knowledgeService.getCrawlProgress(crawlId);
        if (cancelled) {
          return;
        }

        setProgress(next);
        setError(null);

        const done = ['completed', 'failed', 'cancelled'].includes(next.status);
        if (done) {
          if (next.status === 'completed' && onComplete && !notifiedCompleteRef.current) {
            notifiedCompleteRef.current = true;
            onComplete();
          }
          return;
        }

        timer = window.setTimeout(poll, 2000);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch crawl progress');
          timer = window.setTimeout(poll, 2000);
        }
      }
    };

    setProgress(null);
    setError(null);
    notifiedCompleteRef.current = false;
    poll();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [crawlId, onComplete]);

  if (!crawlId) {
    return null;
  }

  return (
    <section
      style={{
        marginBottom: '1.5rem',
        padding: '1rem',
        border: '1px solid #d9e7ff',
        borderRadius: '8px',
        backgroundColor: '#f6f9ff',
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Crawl Progress</div>
      <div style={{ fontSize: '14px', marginBottom: '0.25rem' }}>Status: {progress?.status ?? 'loading'}</div>
      <div style={{ fontSize: '14px', marginBottom: '0.25rem' }}>
        Tasks: {progress?.completed_tasks ?? 0}/{progress?.total_tasks ?? 0} completed
      </div>
      <div style={{ fontSize: '14px', marginBottom: '0.25rem' }}>Failed: {progress?.failed_tasks ?? 0}</div>
      {progress?.current_task_url && (
        <div style={{ fontSize: '13px', color: '#555', wordBreak: 'break-word', marginBottom: '0.25rem' }}>
          Current: {progress.current_task_url}
        </div>
      )}
      {progress?.error && <div style={{ color: '#b42318', fontSize: '13px' }}>{progress.error}</div>}
      {error && <div style={{ color: '#b42318', fontSize: '13px' }}>{error}</div>}
    </section>
  );
};
