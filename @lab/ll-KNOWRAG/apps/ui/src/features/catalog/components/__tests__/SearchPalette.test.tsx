import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ReactNode } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { SearchPalette } from '../SearchPalette'
import { ArtifactSummary } from '../../types'

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
}

function wrap(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <NuqsAdapter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </NuqsAdapter>
  )
}

function baseProps(overrides: Partial<Parameters<typeof SearchPalette>[0]> = {}) {
  return {
    open: true,
    onOpenChange: vi.fn(),
    artifacts: [] as ArtifactSummary[],
    vis: 'public' as const,
    hybrid: false,
    rerank: false,
    onSelect: vi.fn(),
    ...overrides,
  }
}

describe('SearchPalette scope threading', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('POSTs use_hybrid:true and visibility:"private" when those props are set', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ pages: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    const user = userEvent.setup()
    const client = makeClient()
    render(
      <SearchPalette
        {...baseProps({ vis: 'private', hybrid: true, rerank: true })}
      />,
      { wrapper: wrap(client) },
    )

    await user.type(
      screen.getByPlaceholderText(/search artifacts/i),
      'qdrant',
    )

    await waitFor(
      () => {
        expect(globalThis.fetch).toHaveBeenCalled()
      },
      { timeout: 1000 },
    )

    const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls.find(
      (c) => String(c[0]).includes('/api/artifacts/search'),
    )
    expect(call).toBeDefined()
    const init = call?.[1] as RequestInit
    expect(init.method).toBe('POST')
    const body = JSON.parse(String(init.body))
    expect(body.use_hybrid).toBe(true)
    expect(body.use_rerank).toBe(true)
    expect(body.visibility).toBe('private')
    expect(body.query).toBe('qdrant')
  })

  it('POSTs use_hybrid:false and visibility:"public" when props are at defaults', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ pages: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    const user = userEvent.setup()
    const client = makeClient()
    render(<SearchPalette {...baseProps()} />, { wrapper: wrap(client) })

    await user.type(
      screen.getByPlaceholderText(/search artifacts/i),
      'hello',
    )

    await waitFor(
      () => {
        expect(globalThis.fetch).toHaveBeenCalled()
      },
      { timeout: 1000 },
    )

    const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls.find(
      (c) => String(c[0]).includes('/api/artifacts/search'),
    )
    const body = JSON.parse(String((call?.[1] as RequestInit).body))
    expect(body.use_hybrid).toBe(false)
    expect(body.use_rerank).toBe(false)
    expect(body.visibility).toBe('public')
  })

  it('renders the active-modifier caption only when ≥1 modifier is non-default', () => {
    const client = makeClient()
    const { rerender } = render(<SearchPalette {...baseProps()} />, {
      wrapper: wrap(client),
    })
    expect(screen.queryByLabelText(/active search scope/i)).not.toBeInTheDocument()

    rerender(<SearchPalette {...baseProps({ hybrid: true })} />)
    const caption = screen.getByLabelText(/active search scope/i)
    expect(caption).toHaveTextContent('Scope: hybrid')

    rerender(
      <SearchPalette
        {...baseProps({ vis: 'private', hybrid: true, rerank: true })}
      />,
    )
    expect(screen.getByLabelText(/active search scope/i)).toHaveTextContent(
      'Scope: private · hybrid · rerank',
    )
  })
})
