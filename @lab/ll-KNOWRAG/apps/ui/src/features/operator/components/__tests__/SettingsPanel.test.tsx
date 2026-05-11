import { describe, it, expect } from 'vitest'
import { ReactNode } from 'react'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SettingsPanel } from '../SettingsPanel'
import { RAG_LAST_SUCCESS_KEY } from '../../../chat/hooks/useRagQuery'
import type { RagQueryResponse } from '../../../chat/types'

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } })
}

function wrap(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  )
}

describe('SettingsPanel', () => {
  it('shows the empty-state hint when the rag last-success cache is empty', () => {
    const client = makeClient()
    render(<SettingsPanel />, { wrapper: wrap(client) })

    expect(screen.getByText('Active models')).toBeInTheDocument()
    expect(screen.getByText('Send a chat query to populate.')).toBeInTheDocument()
    // All three rows still render — populated rows show "—".
    expect(screen.getByText('chat_provider')).toBeInTheDocument()
    expect(screen.getByText('chat_model')).toBeInTheDocument()
    expect(screen.getByText('embedding_model')).toBeInTheDocument()
  })

  it('renders chat_provider and chat_model from the cache when populated', () => {
    const cached: RagQueryResponse = {
      query: 'q',
      answer: 'a',
      hits: [],
      chat_provider: 'ollama',
      chat_model: 'llama3.2:8b',
    }
    const client = makeClient()
    client.setQueryData(RAG_LAST_SUCCESS_KEY, cached)
    render(<SettingsPanel />, { wrapper: wrap(client) })

    expect(screen.getByText('ollama')).toBeInTheDocument()
    expect(screen.getByText('llama3.2:8b')).toBeInTheDocument()
    // embedding_model has no cache source — always "—" until /api/config lands.
    const embedRow = screen.getByText('embedding_model').closest('div')
    expect(embedRow).not.toBeNull()
    expect(embedRow!.textContent).toContain('—')
    expect(embedRow!.textContent).toContain('Pending GET /api/config')
    // The empty-state hint must NOT render when cache is populated.
    expect(
      screen.queryByText('Send a chat query to populate.'),
    ).not.toBeInTheDocument()
  })
})
