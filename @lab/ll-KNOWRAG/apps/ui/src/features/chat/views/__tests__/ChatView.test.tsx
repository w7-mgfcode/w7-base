import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { ChatView } from '../ChatView'

function renderView() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  window.history.replaceState({}, '', '/')
  return render(
    <NuqsAdapter>
      <QueryClientProvider client={client}>
        <ChatView />
      </QueryClientProvider>
    </NuqsAdapter>,
  )
}

describe('ChatView', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    // jsdom doesn't implement scrollTo
    Element.prototype.scrollTo = vi.fn() as unknown as typeof Element.prototype.scrollTo
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders an empty state on mount with the literal title (Epic 5 grep target)', () => {
    renderView()
    expect(screen.getByText('Ask the knowledge base anything')).toBeInTheDocument()
  })

  it('appends a user message then an assistant message after a successful submit', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({
          query: 'what is knowrag?',
          answer: 'A local-first RAG system.',
          hits: [],
          chat_provider: 'ollama',
          chat_model: 'llama3.2',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    const user = userEvent.setup()
    renderView()

    await user.type(screen.getByLabelText('Chat query'), 'what is knowrag?')
    await user.keyboard('{Meta>}{Enter}{/Meta}')

    // user message appears immediately
    expect(screen.getByText('what is knowrag?')).toBeInTheDocument()

    // assistant message renders after the mutation resolves
    await waitFor(() => {
      expect(screen.getByText('A local-first RAG system.')).toBeInTheDocument()
    })
  })

  it('renders a DegradedNotice when the backend returns 503', async () => {
    ;(globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: {
            error_code: 'chat_provider_unavailable',
            message: 'Provider unreachable at http://ollama:11434',
            retrieved_context: [],
          },
        }),
        { status: 503, headers: { 'Content-Type': 'application/json' } },
      ),
    )
    const user = userEvent.setup()
    renderView()

    await user.type(screen.getByLabelText('Chat query'), 'q')
    await user.keyboard('{Meta>}{Enter}{/Meta}')

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument()
      expect(screen.getByText('Chat provider unreachable')).toBeInTheDocument()
    })
  })
})
