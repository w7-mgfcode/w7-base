import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { ChatMessage } from '../ChatMessage'
import type { ChatMessage as ChatMessageType } from '../../types'

function renderMessage(message: ChatMessageType) {
  return render(
    <NuqsAdapter>
      <ChatMessage message={message} />
    </NuqsAdapter>,
  )
}

describe('ChatMessage', () => {
  it('renders a user message right-aligned with the query text', () => {
    const msg: ChatMessageType = {
      id: '1',
      role: 'user',
      query: 'what is knowrag?',
      createdAt: Date.now(),
    }
    const { container } = renderMessage(msg)
    expect(screen.getByText('what is knowrag?')).toBeInTheDocument()
    expect(container.firstChild).toHaveClass('justify-end')
  })

  it('renders an assistant ok message with answer + sources row', () => {
    const msg: ChatMessageType = {
      id: '2',
      role: 'assistant',
      query: 'what is knowrag?',
      answer: 'KnowRAG is a local-first RAG system.',
      hits: [
        {
          artifact_path: 'knowledge/intro.md',
          chunk_index: 0,
          content: 'KnowRAG is …',
          score: 0.9,
          section_title: null,
          tags: [],
        },
      ],
      createdAt: Date.now(),
    }
    renderMessage(msg)
    expect(
      screen.getByText('KnowRAG is a local-first RAG system.'),
    ).toBeInTheDocument()
    expect(screen.getByText('Sources (1)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Open knowledge\/intro\.md/ })).toBeInTheDocument()
  })

  it('renders an assistant degraded message with the warn-tinted notice', () => {
    const msg: ChatMessageType = {
      id: '3',
      role: 'assistant',
      query: 'q',
      degraded: {
        error_code: 'chat_provider_unavailable',
        message: 'Provider connection refused at http://ollama:11434',
        retrieved_context: [],
      },
      createdAt: Date.now(),
    }
    renderMessage(msg)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    // Label distinguishes the code (label) from the raw provider message body.
    expect(screen.getByText('Chat provider unreachable')).toBeInTheDocument()
    expect(
      screen.getByText('Provider connection refused at http://ollama:11434'),
    ).toBeInTheDocument()
  })

  it('does NOT render a sources row when the assistant has no hits', () => {
    const msg: ChatMessageType = {
      id: '4',
      role: 'assistant',
      query: 'q',
      answer: 'no context for this',
      hits: [],
      createdAt: Date.now(),
    }
    renderMessage(msg)
    expect(screen.queryByText(/^Sources \(/)).not.toBeInTheDocument()
  })
})
