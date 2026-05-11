import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ReactNode } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { HealthCard } from '../HealthCard'

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
}

function wrap(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  )
}

describe('HealthCard', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders a green dot, the service name, and a relative timestamp when healthy', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({ status: 'ok', service: 'knowrag-api' }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    const client = makeClient()
    render(<HealthCard />, { wrapper: wrap(client) })

    // Wait for the post-fetch healthy state — the default service-name label
    // "knowrag-api" is also the loading-state placeholder, so it is not a
    // reliable readiness signal.
    await waitFor(() =>
      expect(screen.getByLabelText('healthy')).toBeInTheDocument(),
    )
    expect(screen.getByText(/System Health/)).toBeInTheDocument()
    expect(screen.getByText('knowrag-api')).toBeInTheDocument()
    // dataUpdatedAt is millis; the relative-time formatter must NOT emit a
    // millisecond-magnitude phrase like "in 1,752,000,000 seconds ago".
    expect(screen.getByTestId('last-checked')).toHaveTextContent(/checked /)
    expect(screen.getByTestId('last-checked').textContent).not.toMatch(
      /\d{6,}/,
    )
  })

  it('renders a red dot when the API call fails', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('boom'),
    )
    const client = makeClient()
    render(<HealthCard />, { wrapper: wrap(client) })

    await waitFor(() =>
      expect(screen.getByLabelText('unhealthy')).toBeInTheDocument(),
    )
  })

  it('renders a red dot when status is not "ok"', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({ status: 'degraded', service: 'knowrag-api' }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    const client = makeClient()
    render(<HealthCard />, { wrapper: wrap(client) })

    await waitFor(() =>
      expect(screen.getByLabelText('unhealthy')).toBeInTheDocument(),
    )
  })
})
