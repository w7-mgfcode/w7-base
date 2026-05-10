import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { ViewTabs } from '../ViewTabs'

function renderWithUrl(initial: string) {
  window.history.replaceState({}, '', initial)
  return render(
    <NuqsAdapter>
      <ViewTabs />
    </NuqsAdapter>,
  )
}

describe('ViewTabs', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
  })

  it('marks Catalog active when ?view= is absent (default)', () => {
    renderWithUrl('/')
    expect(screen.getByRole('tab', { name: 'Catalog' })).toHaveAttribute(
      'data-state',
      'active',
    )
    expect(screen.getByRole('tab', { name: 'Chat' })).toHaveAttribute(
      'data-state',
      'inactive',
    )
  })

  it('marks Chat active when URL is ?view=chat', () => {
    renderWithUrl('/?view=chat')
    expect(screen.getByRole('tab', { name: 'Chat' })).toHaveAttribute(
      'data-state',
      'active',
    )
  })

  it('updates the URL when a trigger is clicked', async () => {
    const user = userEvent.setup()
    renderWithUrl('/')
    await user.click(screen.getByRole('tab', { name: 'Operator' }))
    expect(window.location.search).toContain('view=operator')
  })
})
