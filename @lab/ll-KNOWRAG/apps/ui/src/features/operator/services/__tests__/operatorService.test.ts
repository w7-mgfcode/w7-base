import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { getHealth, postReconcile } from '../operatorService'

describe('operatorService', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('getHealth calls GET /api/health and returns the parsed body', async () => {
    const body = { status: 'ok', service: 'knowrag-api' }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    const result = await getHealth()

    expect(globalThis.fetch).toHaveBeenCalledTimes(1)
    const [url, init] = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    expect(url).toBe('/api/health')
    expect(init).toBeUndefined()
    expect(result).toEqual(body)
  })

  it('postReconcile calls POST /api/ingest/reconcile with no body', async () => {
    const body = { action: 'reconcile', scanned: 12, results: [] }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify(body), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    const result = await postReconcile()

    expect(globalThis.fetch).toHaveBeenCalledTimes(1)
    const [url, init] = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    expect(url).toBe('/api/ingest/reconcile')
    expect(init).toMatchObject({ method: 'POST' })
    // Per the API contract, reconcile takes no body.
    expect((init as RequestInit | undefined)?.body).toBeUndefined()
    expect(result).toEqual(body)
  })

  it('postReconcile surfaces non-2xx responses as Error', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response('boom', { status: 500, statusText: 'Internal Server Error' }),
    )

    await expect(postReconcile()).rejects.toThrow(/^500 Internal Server Error/)
  })
})
