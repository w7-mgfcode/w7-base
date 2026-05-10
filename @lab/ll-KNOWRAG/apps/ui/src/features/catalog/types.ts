// Phase 8 artifact types — match the API server's Pydantic models
// (server/models/storage.py, server/services/knowledge/frontmatter.py).

export const STATUS_VALUES = ['draft', 'review', 'published'] as const
export type Status = (typeof STATUS_VALUES)[number]

export const VISIBILITY_VALUES = ['public', 'private'] as const
export type Visibility = (typeof VISIBILITY_VALUES)[number]

export const ARTIFACT_CATEGORIES = [
  'prompts',
  'commands',
  'mcp',
  'hooks',
  'skills',
  'knowledge',
] as const

export type ArtifactCategory = (typeof ARTIFACT_CATEGORIES)[number]

export interface Frontmatter {
  id: string
  owner: string
  tags: string[]
  status: Status
  version: string
  visibility: Visibility
  created_at?: string | null
  updated_at?: string | null
  // Frontmatter is `extra=allow` server-side — preserve unknown keys.
  [key: string]: unknown
}

export interface ArtifactSummary {
  path: string
  frontmatter: Frontmatter
  commit_sha: string
  size: number
}

export interface Artifact extends ArtifactSummary {
  body: string
}

export interface RelatedArtifact {
  artifact_path: string
  score: number
  section_title?: string | null
  snippet: string
  tags: string[]
  status?: Status | null
  owner?: string | null
  shared_tags: string[]
}

export interface SearchHit {
  artifact_path: string
  chunk_index: number
  content: string
  score: number
  section_title?: string | null
  commit_sha: string
  tags: string[]
  status?: Status | null
  owner?: string | null
}

export interface SearchPage {
  artifact_path: string
  top_score: number
  top_chunk_index: number
  section_titles: string[]
  chunk_count: number
  owner?: string | null
  tags: string[]
}

export interface SearchResponse {
  hits: SearchHit[]
  pages?: SearchPage[]
}

export interface FilterState {
  category: ArtifactCategory | null
  tags: string[]
  status: Status[]
  owner: string | null
  query: string
}

export function categoryFromPath(path: string): ArtifactCategory | null {
  const head = path.split('/')[0]
  return (ARTIFACT_CATEGORIES as readonly string[]).includes(head)
    ? (head as ArtifactCategory)
    : null
}
