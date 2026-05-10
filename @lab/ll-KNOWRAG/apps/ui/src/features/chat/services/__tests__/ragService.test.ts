import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { postRagQuery } from '../ragService'
import type { RagQueryResponse } from '../../types'

const REQ = { query: 'what is knowrag?' }

function mockResponse(body: unknown, init: ResponseInit) {
  return new Response(JSON.stringify(body), {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init.headers ?? {}) },
  })
}

describe('postRagQuery', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns ok:true with parsed RagQueryResponse on 200', async () => {
    const payload: RagQueryResponse = {
      query: 'q',
      answer: 'a',
      hits: [],
      chat_provider: 'ollama',
      chat_model: 'llama3.2',
    }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse(payload, { status: 200 }),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.data).toEqual(payload)
    }
  })

  it('returns degraded branch on 503 chat_provider_unavailable', async () => {
    const detail = {
      error_code: 'chat_provider_unavailable',
      message: 'provider unreachable',
      retrieved_context: [
        {
          artifact_path: 'knowledge/x.md',
          chunk_index: 0,
          content: 'snippet',
          score: 0.42,
          section_title: null,
          tags: [],
        },
      ],
    }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse({ detail }, { status: 503, statusText: 'Service Unavailable' }),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(false)
    if (!result.ok && 'degraded' in result) {
      expect(result.degraded.error_code).toBe('chat_provider_unavailable')
      expect(result.degraded.retrieved_context).toHaveLength(1)
    } else {
      throw new Error('expected degraded branch')
    }
  })

  it('returns degraded branch on 503 chat_model_unavailable', async () => {
    const detail = {
      error_code: 'chat_model_unavailable',
      message: 'pull the model with: docker exec -it knowrag-ollama ollama pull llama3.2',
      retrieved_context: [],
    }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse({ detail }, { status: 503 }),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(false)
    if (!result.ok && 'degraded' in result) {
      expect(result.degraded.error_code).toBe('chat_model_unavailable')
      expect(result.degraded.message).toContain('docker exec')
    } else {
      throw new Error('expected degraded branch')
    }
  })

  it('returns error branch on 500', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response('boom', { status: 500, statusText: 'Internal Server Error' }),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(false)
    if (!result.ok && 'error' in result) {
      expect(result.error.message).toMatch(/^500 Internal Server Error/)
    } else {
      throw new Error('expected error branch')
    }
  })

  it('returns error branch when fetch throws (network error)', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
      new TypeError('Failed to fetch'),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(false)
    if (!result.ok && 'error' in result) {
      expect(result.error.message).toContain('network error')
      expect(result.error.message).toContain('Failed to fetch')
    } else {
      throw new Error('expected error branch')
    }
  })

  it('falls back to error when 503 detail is a plain string (FastAPI default)', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      mockResponse(
        { detail: 'Service Unavailable' },
        { status: 503, statusText: 'Service Unavailable' },
      ),
    )

    const result = await postRagQuery(REQ)

    expect(result.ok).toBe(false)
    if (!result.ok && 'error' in result) {
      expect(result.error.message).toMatch(/^503/)
    } else {
      throw new Error('expected error branch for stringified detail')
    }
  })
})
