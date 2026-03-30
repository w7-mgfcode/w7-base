export interface Source {
  source_id: string;
  source_url?: string;
  source_display_name?: string;
  title?: string;
  summary?: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Page {
  id: string;
  source_id: string;
  url: string;
  full_content: string;
  section_title?: string;
  section_order: number;
  word_count: number;
  char_count: number;
  metadata: Record<string, any>;
  created_at: string;
}

export interface ChunkSearchResult {
  id: number;
  source_id: string;
  page_id?: string;
  content: string;
  metadata: Record<string, any>;
  similarity: number;
  url?: string;
}

export interface PageSearchResult {
  page_id: string;
  source_id: string;
  url: string;
  title?: string;
  summary?: string;
  max_similarity: number;
  chunk_count: number;
  chunks: ChunkSearchResult[];
}

export interface SearchResponse {
  query: string;
  mode: 'chunk' | 'page';
  results: ChunkSearchResult[] | PageSearchResult[];
  total_results: number;
  processing_time_ms: number;
}

export interface CrawlProgress {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  current_task_url?: string | null;
  results: Record<string, any>[];
  error?: string | null;
}
