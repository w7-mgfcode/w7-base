import { useEffect, useRef, useState } from 'react'
import { MessageCircle } from 'lucide-react'
import { EmptyState } from '../../../components/ui/EmptyState'
import { Spinner } from '../../../components/ui/Spinner'
import { ChatComposer } from '../components/ChatComposer'
import { ChatMessage } from '../components/ChatMessage'
import { useRagQuery } from '../hooks/useRagQuery'
import type {
  AssistantChatMessage,
  ChatMessage as ChatMessageType,
  RagQueryRequest,
  UserChatMessage,
} from '../types'

function makeId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

export function ChatView() {
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const threadRef = useRef<HTMLElement | null>(null)
  const mutation = useRagQuery()

  // Auto-scroll: smooth only when a new assistant message lands (response feels
  // alive); instant for the user's own append (no animation needed for input
  // they just typed). Skip when already at the bottom to avoid stacking smooth
  // animations on rapid appends.
  const lastRole = messages[messages.length - 1]?.role
  useEffect(() => {
    const el = threadRef.current
    if (!el || messages.length === 0) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    if (distanceFromBottom < 4) return
    el.scrollTo({
      top: el.scrollHeight,
      behavior: lastRole === 'assistant' ? 'smooth' : 'auto',
    })
  }, [messages.length, lastRole])

  function handleSubmitMessage(req: RagQueryRequest) {
    const now = Date.now()
    const userMsg: UserChatMessage = {
      id: makeId(),
      role: 'user',
      query: req.query,
      createdAt: now,
    }
    setMessages((prev) => [...prev, userMsg])

    mutation.mutate(req, {
      onSuccess: (result) => {
        const assistantMsg: AssistantChatMessage = result.ok
          ? {
              id: makeId(),
              role: 'assistant',
              query: req.query,
              answer: result.data.answer,
              hits: result.data.hits,
              createdAt: Date.now(),
            }
          : 'degraded' in result
            ? {
                id: makeId(),
                role: 'assistant',
                query: req.query,
                degraded: result.degraded,
                createdAt: Date.now(),
              }
            : {
                id: makeId(),
                role: 'assistant',
                query: req.query,
                answer: `**Error:** ${result.error.message}`,
                createdAt: Date.now(),
              }
        setMessages((prev) => [...prev, assistantMsg])
      },
      onError: (err) => {
        const assistantMsg: AssistantChatMessage = {
          id: makeId(),
          role: 'assistant',
          query: req.query,
          answer: `**Error:** ${err.message}`,
          createdAt: Date.now(),
        }
        setMessages((prev) => [...prev, assistantMsg])
      },
    })
  }

  return (
    <div className="flex flex-col h-full">
      <main
        ref={threadRef as React.RefObject<HTMLElement>}
        className="flex-1 overflow-y-auto p-4"
      >
        {messages.length === 0 && !mutation.isPending ? (
          <EmptyState
            icon={<MessageCircle size={48} />}
            title="Ask the knowledge base anything"
            description="Type a question and press ⌘+Enter or Ctrl+Enter to send."
          />
        ) : (
          <div className="mx-auto max-w-3xl space-y-3">
            {messages.map((m) => (
              <ChatMessage key={m.id} message={m} />
            ))}
            {mutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-surface-1 rounded-card px-4 py-3 border border-hairline inline-flex items-center gap-2 text-fg-muted text-sm">
                  <Spinner />
                  <span>Thinking…</span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
      <ChatComposer
        onSubmitMessage={handleSubmitMessage}
        isPending={mutation.isPending}
      />
    </div>
  )
}
