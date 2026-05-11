import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { ReactNode } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { CatalogView } from '../CatalogView'

function makeClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
}

function renderWithUrl(initial: string) {
  window.history.replaceState({}, '', initial)
  const client = makeClient()
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <NuqsAdapter>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </NuqsAdapter>
  )
  return render(<CatalogView />, { wrapper: Wrapper })
}

describe('CatalogView URL round-trip', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('hydrates Scope subsection from ?vis=private&hybrid=true&rerank=true', async () => {
    renderWithUrl('/?vis=private&hybrid=true&rerank=true')

    await waitFor(() => {
      expect(
        screen.getByRole('radio', { name: 'private' }),
      ).toHaveAttribute('data-state', 'on')
    })
    expect(screen.getByRole('switch', { name: 'hybrid' })).toHaveAttribute(
      'data-state',
      'checked',
    )
    expect(screen.getByRole('switch', { name: 'rerank' })).toHaveAttribute(
      'data-state',
      'checked',
    )
  })

  it('uses defaults (public / hybrid off / rerank off) when params are absent', async () => {
    renderWithUrl('/')

    await waitFor(() => {
      expect(
        screen.getByRole('radio', { name: 'public' }),
      ).toHaveAttribute('data-state', 'on')
    })
    expect(screen.getByRole('switch', { name: 'hybrid' })).toHaveAttribute(
      'data-state',
      'unchecked',
    )
    expect(screen.getByRole('switch', { name: 'rerank' })).toHaveAttribute(
      'data-state',
      'unchecked',
    )
  })

  it('treats invalid ?vis=foo as the default (public)', async () => {
    renderWithUrl('/?vis=foo')

    await waitFor(() => {
      expect(
        screen.getByRole('radio', { name: 'public' }),
      ).toHaveAttribute('data-state', 'on')
    })
  })

  it('clicking a Scope toggle updates the URL', async () => {
    const user = userEvent.setup()
    renderWithUrl('/')

    await waitFor(() => {
      expect(screen.getByRole('switch', { name: 'hybrid' })).toBeInTheDocument()
    })
    await user.click(screen.getByRole('switch', { name: 'hybrid' }))
    await waitFor(() => {
      expect(window.location.search).toContain('hybrid=true')
    })
  })

  it('Clear button (when present) resets all six filters including scope', async () => {
    const user = userEvent.setup()
    renderWithUrl(
      '/?cat=prompts&vis=private&hybrid=true&rerank=true',
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Clear/i })).toBeInTheDocument()
    })
    await user.click(screen.getByRole('button', { name: /Clear/i }))
    await waitFor(() => {
      // After clear, the URL should not carry the scope modifiers
      expect(window.location.search).not.toContain('vis=private')
      expect(window.location.search).not.toContain('hybrid=true')
      expect(window.location.search).not.toContain('rerank=true')
      expect(window.location.search).not.toContain('cat=prompts')
    })
  })
})
