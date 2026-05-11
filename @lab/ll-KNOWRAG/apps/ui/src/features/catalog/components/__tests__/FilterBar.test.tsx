import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FilterBar } from '../FilterBar'
import { ArtifactSummary } from '../../types'

function baseProps(overrides: Partial<Parameters<typeof FilterBar>[0]> = {}) {
  return {
    artifacts: [] as ArtifactSummary[],
    category: null,
    tags: [],
    status: [],
    owner: null,
    vis: 'public' as const,
    hybrid: false,
    rerank: false,
    onCategoryChange: vi.fn(),
    onTagsChange: vi.fn(),
    onStatusChange: vi.fn(),
    onOwnerChange: vi.fn(),
    onVisChange: vi.fn(),
    onHybridChange: vi.fn(),
    onRerankChange: vi.fn(),
    onClearAll: vi.fn(),
    ...overrides,
  }
}

describe('FilterBar Scope subsection', () => {
  it('renders Scope label, visibility toggle, hybrid + rerank switches', () => {
    render(<FilterBar {...baseProps()} />)
    expect(screen.getByText('Scope')).toBeInTheDocument()
    expect(screen.getByRole('group', { name: /visibility/i })).toBeInTheDocument()
    expect(screen.getByRole('switch', { name: 'hybrid' })).toBeInTheDocument()
    expect(screen.getByRole('switch', { name: 'rerank' })).toBeInTheDocument()
  })

  it('reflects initial vis/hybrid/rerank from props', () => {
    render(
      <FilterBar
        {...baseProps({ vis: 'private', hybrid: true, rerank: true })}
      />,
    )
    expect(screen.getByRole('switch', { name: 'hybrid' })).toHaveAttribute(
      'data-state',
      'checked',
    )
    expect(screen.getByRole('switch', { name: 'rerank' })).toHaveAttribute(
      'data-state',
      'checked',
    )
    expect(
      screen.getByRole('radio', { name: 'private' }),
    ).toHaveAttribute('data-state', 'on')
  })

  it('invokes onVisChange when clicking visibility item', async () => {
    const user = userEvent.setup()
    const onVisChange = vi.fn()
    render(<FilterBar {...baseProps({ onVisChange })} />)
    await user.click(screen.getByRole('radio', { name: 'private' }))
    expect(onVisChange).toHaveBeenCalledWith('private')
  })

  it('invokes onHybridChange when toggling hybrid switch', async () => {
    const user = userEvent.setup()
    const onHybridChange = vi.fn()
    render(<FilterBar {...baseProps({ onHybridChange })} />)
    await user.click(screen.getByRole('switch', { name: 'hybrid' }))
    expect(onHybridChange).toHaveBeenCalledWith(true)
  })

  it('invokes onRerankChange when toggling rerank switch', async () => {
    const user = userEvent.setup()
    const onRerankChange = vi.fn()
    render(<FilterBar {...baseProps({ rerank: true, onRerankChange })} />)
    await user.click(screen.getByRole('switch', { name: 'rerank' }))
    expect(onRerankChange).toHaveBeenCalledWith(false)
  })

  it('does not use solid bg-status-{ok,warn,err} fills in the Scope subsection', () => {
    const { container } = render(<FilterBar {...baseProps()} />)
    const html = container.innerHTML
    expect(html).not.toMatch(/\bbg-status-(ok|warn|err)\b(?!\/)/)
  })

  it('shows the Clear button when only scope filters are non-default', () => {
    const { rerender } = render(<FilterBar {...baseProps()} />)
    expect(
      screen.queryByRole('button', { name: /Clear/i }),
    ).not.toBeInTheDocument()

    rerender(<FilterBar {...baseProps({ vis: 'private' })} />)
    expect(
      screen.getByRole('button', { name: /Clear \(1\)/i }),
    ).toBeInTheDocument()

    rerender(<FilterBar {...baseProps({ hybrid: true })} />)
    expect(
      screen.getByRole('button', { name: /Clear \(1\)/i }),
    ).toBeInTheDocument()

    rerender(
      <FilterBar
        {...baseProps({ vis: 'private', hybrid: true, rerank: true })}
      />,
    )
    expect(
      screen.getByRole('button', { name: /Clear \(3\)/i }),
    ).toBeInTheDocument()
  })
})
