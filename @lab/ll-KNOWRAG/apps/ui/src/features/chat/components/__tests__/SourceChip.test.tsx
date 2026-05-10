import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { SourceChip } from '../SourceChip'
import type { RagQueryHit } from '../../types'

const HIT: RagQueryHit = {
  artifact_path: 'knowledge/getting-started.md',
  chunk_index: 0,
  content: 'KnowRAG is a local-first knowledge-base + RAG system.',
  score: 0.91,
  section_title: 'Overview',
  tags: ['rag', 'qdrant'],
}

function renderChip(initial = '/') {
  window.history.replaceState({}, '', initial)
  return render(
    <NuqsAdapter>
      <SourceChip hit={HIT} index={1} />
    </NuqsAdapter>,
  )
}

describe('SourceChip', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
  })

  it('renders the bracketed index and the artifact basename', () => {
    renderChip()
    expect(screen.getByRole('button')).toHaveTextContent('[1]')
    expect(screen.getByRole('button')).toHaveTextContent('getting-started.md')
  })

  it('navigates away from chat to catalog (the default view) and sets the artifact path', async () => {
    const user = userEvent.setup()
    renderChip('/?view=chat')
    await user.click(screen.getByRole('button'))
    // catalog is the default `view`, so nuqs strips it from the URL —
    // the contract is "no longer on chat" + "artifact path is set".
    expect(window.location.search).not.toContain('view=chat')
    expect(window.location.search).toMatch(/a=knowledge(%2F|\/)getting-started\.md/)
  })
})
