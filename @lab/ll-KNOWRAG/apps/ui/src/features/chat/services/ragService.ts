import type {
  DegradedDetail,
  DegradedErrorCode,
  RagQueryRequest,
  RagQueryResponse,
} from '../types'

export type RagQueryResult =
  | { ok: true; data: RagQueryResponse }
  | { ok: false; degraded: DegradedDetail }
  | { ok: false; error: Error }

const DEGRADED_CODES: ReadonlySet<DegradedErrorCode> = new Set([
  'chat_provider_unavailable',
  'chat_model_unavailable',
])

function isDegradedDetail(value: unknown): value is DegradedDetail {
  if (typeof value !== 'object' || value === null) return false
  const v = value as Record<string, unknown>
  return (
    typeof v.error_code === 'string' &&
    DEGRADED_CODES.has(v.error_code as DegradedErrorCode) &&
    typeof v.message === 'string' &&
    Array.isArray(v.retrieved_context)
  )
}

export async function postRagQuery(
  req: RagQueryRequest,
): Promise<RagQueryResult> {
  let res: Response
  try {
    res = await fetch('/api/rag/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    })
  } catch (cause) {
    return {
      ok: false,
      error: new Error(
        `network error — ${cause instanceof Error ? cause.message : String(cause)}`,
      ),
    }
  }

  if (res.ok) {
    const data = (await res.json()) as RagQueryResponse
    return { ok: true, data }
  }

  if (res.status === 503) {
    try {
      const body = (await res.json()) as { detail?: unknown }
      if (isDegradedDetail(body.detail)) {
        return { ok: false, degraded: body.detail }
      }
    } catch {
      // fall through to generic error
    }
  }

  const text = await res.text().catch(() => '')
  return {
    ok: false,
    error: new Error(
      `${res.status} ${res.statusText}${text ? ` — ${text}` : ''}`,
    ),
  }
}
