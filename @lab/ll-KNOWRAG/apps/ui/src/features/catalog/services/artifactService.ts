import {
  Artifact,
  ArtifactCategory,
  ArtifactSummary,
  RelatedArtifact,
  SearchResponse,
  Status,
} from '../types'
import { fetchJson } from '../../../lib/api'

const API_BASE = ''

export async function listArtifacts(
  category?: ArtifactCategory,
): Promise<ArtifactSummary[]> {
  const url = new URL(`${API_BASE}/api/artifacts`, window.location.origin)
  if (category) url.searchParams.set('category', category)
  return fetchJson<ArtifactSummary[]>(url.pathname + url.search)
}

export async function getArtifact(path: string, ref?: string): Promise<Artifact> {
  const url = new URL(
    `${API_BASE}/api/artifacts/${path}`,
    window.location.origin,
  )
  if (ref) url.searchParams.set('ref', ref)
  return fetchJson<Artifact>(url.pathname + url.search)
}

export async function getRelatedArtifacts(
  path: string,
  k = 5,
  visibility: 'public' | 'private' = 'public',
): Promise<RelatedArtifact[]> {
  const url = new URL(
    `${API_BASE}/api/artifacts/${path}/related`,
    window.location.origin,
  )
  url.searchParams.set('k', String(k))
  url.searchParams.set('visibility', visibility)
  return fetchJson<RelatedArtifact[]>(url.pathname + url.search)
}

export interface SearchArgs {
  query: string
  tags?: string[]
  status?: Status[]
  owner?: string
  visibility?: 'public' | 'private'
  topK?: number
  useHybrid?: boolean
  useRerank?: boolean
}

export async function searchArtifacts(args: SearchArgs): Promise<SearchResponse> {
  return fetchJson<SearchResponse>(`${API_BASE}/api/artifacts/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: args.query,
      tags: args.tags,
      status: args.status,
      owner: args.owner,
      visibility: args.visibility ?? 'public',
      top_k: args.topK ?? 20,
      use_hybrid: args.useHybrid ?? false,
      use_rerank: args.useRerank ?? false,
    }),
  })
}
