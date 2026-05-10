import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { DegradedNotice } from '../DegradedNotice'
import type { DegradedDetail } from '../../types'

function renderNotice(detail: DegradedDetail) {
  return render(
    <NuqsAdapter>
      <DegradedNotice detail={detail} />
    </NuqsAdapter>,
  )
}

describe('DegradedNotice', () => {
  it('renders a warn-tinted alert with the message', () => {
    const detail: DegradedDetail = {
      error_code: 'chat_provider_unavailable',
      message: 'Chat provider unreachable. Start Ollama.',
      retrieved_context: [],
    }
    renderNotice(detail)
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('bg-status-warn/10')
    expect(alert).toHaveClass('text-status-warn')
    expect(alert).not.toHaveClass('bg-status-warn')
    expect(screen.getByText('Chat provider unreachable')).toBeInTheDocument()
  })

  it('renders the copy-command button when the message contains a docker exec hint', () => {
    const detail: DegradedDetail = {
      error_code: 'chat_model_unavailable',
      message:
        "Chat model 'llama3.2' is not available. Pull it with: docker exec -it knowrag-ollama ollama pull llama3.2.",
      retrieved_context: [],
    }
    renderNotice(detail)
    expect(screen.getByRole('button', { name: 'Copy command' })).toBeInTheDocument()
    // the standalone <code> block holds the trimmed command exactly
    const codeBlock = screen
      .getAllByText(/docker exec -it knowrag-ollama ollama pull llama3\.2/)
      .find((el) => el.tagName === 'CODE')
    expect(codeBlock).toBeDefined()
    expect(codeBlock?.textContent).toBe(
      'docker exec -it knowrag-ollama ollama pull llama3.2',
    )
  })

  it('renders retrieved-context chips when present', () => {
    const detail: DegradedDetail = {
      error_code: 'chat_provider_unavailable',
      message: 'down',
      retrieved_context: [
        {
          artifact_path: 'knowledge/a.md',
          chunk_index: 0,
          content: 'one',
          score: 0.5,
          section_title: null,
          tags: [],
        },
        {
          artifact_path: 'knowledge/b.md',
          chunk_index: 1,
          content: 'two',
          score: 0.4,
          section_title: null,
          tags: [],
        },
      ],
    }
    renderNotice(detail)
    expect(screen.getByText('Retrieved context (2)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Open knowledge\/a\.md/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Open knowledge\/b\.md/ })).toBeInTheDocument()
  })
})
