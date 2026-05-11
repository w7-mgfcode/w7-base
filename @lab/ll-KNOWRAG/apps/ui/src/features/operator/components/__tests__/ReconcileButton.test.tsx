import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ReactNode } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReconcileButton } from '../ReconcileButton'

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
}

function wrap(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  )
}

describe('ReconcileButton', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('opens an AlertDialog before firing the mutation', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ action: 'reconcile', scanned: 0, results: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    const user = userEvent.setup()
    const client = makeClient()
    render(<ReconcileButton />, { wrapper: wrap(client) })

    // Mutation must NOT fire before confirmation.
    expect(globalThis.fetch).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /Reconcile Git/ }))
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
    expect(globalThis.fetch).not.toHaveBeenCalled()
  })

  it('fires reconcile exactly once on confirm and surfaces the scanned count', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({ action: 'reconcile', scanned: 17, results: [] }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    const user = userEvent.setup()
    const client = makeClient()
    render(<ReconcileButton />, { wrapper: wrap(client) })

    await user.click(screen.getByRole('button', { name: /Reconcile Git/ }))
    await user.click(screen.getByRole('button', { name: /Confirm reconcile/ }))

    await waitFor(() =>
      expect(
        screen.getByText(/Reconcile complete — scanned 17 artifacts\./),
      ).toBeInTheDocument(),
    )
    expect(globalThis.fetch).toHaveBeenCalledTimes(1)
    const [url, init] = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0]
    expect(url).toBe('/api/ingest/reconcile')
    expect((init as RequestInit).method).toBe('POST')
  })

  it('disables the trigger button while a mutation is pending', async () => {
    let resolveFetch: (v: Response) => void = () => {}
    const pending = new Promise<Response>((r) => {
      resolveFetch = r
    })
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockReturnValue(pending)

    const user = userEvent.setup()
    const client = makeClient()
    render(<ReconcileButton />, { wrapper: wrap(client) })

    await user.click(screen.getByRole('button', { name: /Reconcile Git/ }))
    await user.click(screen.getByRole('button', { name: /Confirm reconcile/ }))

    await waitFor(() =>
      expect(screen.getByRole('button', { name: /Reconcile Git/ })).toBeDisabled(),
    )

    resolveFetch(
      new Response(JSON.stringify({ action: 'reconcile', scanned: 1, results: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
  })

  it('shows a red error notice when the reconcile call fails', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response('boom', { status: 500, statusText: 'Internal Server Error' }),
    )
    const user = userEvent.setup()
    const client = makeClient()
    render(<ReconcileButton />, { wrapper: wrap(client) })

    await user.click(screen.getByRole('button', { name: /Reconcile Git/ }))
    await user.click(screen.getByRole('button', { name: /Confirm reconcile/ }))

    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent(/Reconcile failed/),
    )
  })
})
