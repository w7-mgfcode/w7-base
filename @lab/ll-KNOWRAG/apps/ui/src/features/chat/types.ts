import type { Status, Visibility } from '../catalog/types'

// Mirrors apps/api/src/server/api_routes/rag_api.py:35-60
// Backend constraints: match_count Field(default=5, ge=1, le=50).

export interface RagQueryRequest {
  query: string
  visibility?: Visibility
  tags?: string[]
  status?: Status[]
  owner?: string | null
  match_count?: number
  use_hybrid?: boolean
  use_rerank?: boolean
}

export interface RagQueryHit {
  artifact_path: string
  chunk_index: number
  content: string
  score: number
  section_title?: string | null
  tags: string[]
}

export interface RagQueryResponse {
  query: string
  answer: string
  hits: RagQueryHit[]
  chat_provider: string
  chat_model: string
}

export type DegradedErrorCode =
  | 'chat_provider_unavailable'
  | 'chat_model_unavailable'

export interface DegradedDetail {
  error_code: DegradedErrorCode
  message: string
  retrieved_context: RagQueryHit[]
}

export interface UserChatMessage {
  id: string
  role: 'user'
  query: string
  createdAt: number
}

export interface AssistantChatMessage {
  id: string
  role: 'assistant'
  query: string
  answer?: string
  hits?: RagQueryHit[]
  degraded?: DegradedDetail
  createdAt: number
}

export type ChatMessage = UserChatMessage | AssistantChatMessage
