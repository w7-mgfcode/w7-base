import { fetchJson } from '../../../lib/api'

export interface HealthResponse {
  status: string
  service: string
}

export interface ReconcileResponse {
  action: string
  scanned: number
  results: unknown[]
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchJson<HealthResponse>('/api/health')
}

export async function postReconcile(): Promise<ReconcileResponse> {
  return fetchJson<ReconcileResponse>('/api/ingest/reconcile', { method: 'POST' })
}
