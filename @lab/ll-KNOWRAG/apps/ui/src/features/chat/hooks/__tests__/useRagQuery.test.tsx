import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ReactNode } from 'react'
import { renderHook, waitFor, act } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RAG_LAST_SUCCESS_KEY, useRagQuery } from '../useRagQuery'
import type { RagQueryResponse } from '../../types'

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
}

function wrapper(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  )
}

const REQ = { query: 'hello?' }

describe('useRagQuery', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('mutates to ok:true and writes the response into the last-success cache', async () => {
    const payload: RagQueryResponse = {
      query: 'hello?',
      answer: 'world',
      hits: [],
      chat_provider: 'ollama',
      chat_model: 'llama3.2',
    }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    const client = makeClient()
    const { result } = renderHook(() => useRagQuery(), { wrapper: wrapper(client) })

    await act(async () => {
      result.current.mutate(REQ)
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual({ ok: true, data: payload })
    expect(client.getQueryData(RAG_LAST_SUCCESS_KEY)).toEqual(payload)
  })

  it('does NOT write to the last-success cache when the response is degraded', async () => {
    const detail = {
      error_code: 'chat_provider_unavailable',
      message: 'down',
      retrieved_context: [],
    }
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ detail }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    const client = makeClient()
    const { result } = renderHook(() => useRagQuery(), { wrapper: wrapper(client) })

    await act(async () => {
      result.current.mutate(REQ)
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(client.getQueryData(RAG_LAST_SUCCESS_KEY)).toBeUndefined()
  })

  it('toggles isPending true then false across a mutation', async () => {
    let resolveFetch: (v: Response) => void = () => {}
    const pending = new Promise<Response>((r) => {
      resolveFetch = r
    })
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockReturnValue(pending)

    const client = makeClient()
    const { result } = renderHook(() => useRagQuery(), { wrapper: wrapper(client) })

    expect(result.current.isPending).toBe(false)

    act(() => {
      result.current.mutate(REQ)
    })
    await waitFor(() => expect(result.current.isPending).toBe(true))

    await act(async () => {
      resolveFetch(
        new Response(
          JSON.stringify({
            query: 'q',
            answer: 'a',
            hits: [],
            chat_provider: 'ollama',
            chat_model: 'llama3.2',
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      )
    })

    await waitFor(() => expect(result.current.isPending).toBe(false))
  })
})
