import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NuqsAdapter } from 'nuqs/adapters/react'
import { ChatComposer } from '../ChatComposer'

function renderComposer(props: {
  onSubmitMessage?: ReturnType<typeof vi.fn>
  isPending?: boolean
  initialUrl?: string
} = {}) {
  const onSubmitMessage = props.onSubmitMessage ?? vi.fn()
  window.history.replaceState({}, '', props.initialUrl ?? '/')
  const utils = render(
    <NuqsAdapter>
      <ChatComposer
        onSubmitMessage={onSubmitMessage}
        isPending={props.isPending ?? false}
      />
    </NuqsAdapter>,
  )
  return { ...utils, onSubmitMessage }
}

describe('ChatComposer', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
  })

  it('submits via Cmd+Enter with the typed query and default scope', async () => {
    const user = userEvent.setup()
    const { onSubmitMessage } = renderComposer()
    const textarea = screen.getByLabelText('Chat query')
    await user.type(textarea, 'what is knowrag?')
    await user.keyboard('{Meta>}{Enter}{/Meta}')
    expect(onSubmitMessage).toHaveBeenCalledTimes(1)
    expect(onSubmitMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'what is knowrag?',
        visibility: 'public',
        use_hybrid: false,
        use_rerank: false,
      }),
    )
  })

  it('submits via Ctrl+Enter (cross-OS)', async () => {
    const user = userEvent.setup()
    const { onSubmitMessage } = renderComposer()
    await user.type(screen.getByLabelText('Chat query'), 'hello')
    await user.keyboard('{Control>}{Enter}{/Control}')
    expect(onSubmitMessage).toHaveBeenCalledTimes(1)
  })

  it('does NOT submit on a plain Enter (it inserts a newline)', async () => {
    const user = userEvent.setup()
    const { onSubmitMessage } = renderComposer()
    const textarea = screen.getByLabelText('Chat query') as HTMLTextAreaElement
    await user.type(textarea, 'line 1')
    await user.keyboard('{Enter}')
    await user.type(textarea, 'line 2')
    expect(onSubmitMessage).not.toHaveBeenCalled()
    expect(textarea.value).toContain('\n')
  })

  it('disables textarea and Ask button while isPending=true', () => {
    renderComposer({ isPending: true })
    expect(screen.getByLabelText('Chat query')).toBeDisabled()
    expect(screen.getByRole('button', { name: /Ask/ })).toBeDisabled()
  })

  it('reads vis / hybrid / rerank scope from the URL and forwards them in the request', async () => {
    const user = userEvent.setup()
    const { onSubmitMessage } = renderComposer({
      initialUrl: '/?vis=private&hybrid=true&rerank=true',
    })
    await user.type(screen.getByLabelText('Chat query'), 'scoped query')
    await user.keyboard('{Meta>}{Enter}{/Meta}')
    expect(onSubmitMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        query: 'scoped query',
        visibility: 'private',
        use_hybrid: true,
        use_rerank: true,
      }),
    )
    // Active-scope summary is rendered above the textarea.
    expect(screen.getByText(/Scope:/)).toBeInTheDocument()
  })
})
