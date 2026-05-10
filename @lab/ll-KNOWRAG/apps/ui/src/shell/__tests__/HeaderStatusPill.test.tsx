import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HeaderStatusPill } from '../HeaderStatusPill'

function renderPill() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <HeaderStatusPill />
    </QueryClientProvider>,
  )
}

describe('HeaderStatusPill', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders red and "API down" when /api/health returns 500', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response('boom', { status: 500, statusText: 'Internal Server Error' }),
    )
    renderPill()
    await waitFor(() => {
      expect(screen.getByText('API down')).toBeInTheDocument()
    })
    expect(screen.getByRole('status').querySelector('svg')).toHaveClass(
      'text-status-err',
    )
  })

  it('renders green and "API ok" when /api/health returns {status: "ok"}', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok', service: 'knowrag-api' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    renderPill()
    await waitFor(() => {
      expect(screen.getByText('API ok')).toBeInTheDocument()
    })
    expect(screen.getByRole('status').querySelector('svg')).toHaveClass(
      'text-status-ok',
    )
  })
})
