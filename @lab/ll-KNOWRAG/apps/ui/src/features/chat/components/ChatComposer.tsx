import { FormEvent, KeyboardEvent, useState } from 'react'
import { Send } from 'lucide-react'
import {
  parseAsArrayOf,
  parseAsBoolean,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from 'nuqs'
import { Button } from '../../../components/ui/Button'
import type { RagQueryRequest } from '../types'
import type { Status, Visibility } from '../../catalog/types'

const VISIBILITY_VALUES = ['public', 'private'] as const
const STATUS_VALUES = ['draft', 'review', 'published'] as const

interface ChatComposerProps {
  onSubmitMessage: (req: RagQueryRequest) => void
  isPending: boolean
}

export function ChatComposer({ onSubmitMessage, isPending }: ChatComposerProps) {
  const [query, setQuery] = useState('')

  // Scope reads — these URL params are introduced by Epic 4 (#59); until
  // they exist on the catalog FilterBar, defaults apply (public / off / off).
  const [scope] = useQueryStates({
    vis: parseAsStringLiteral(VISIBILITY_VALUES).withDefault('public'),
    hybrid: parseAsBoolean.withDefault(false),
    rerank: parseAsBoolean.withDefault(false),
    tags: parseAsArrayOf(parseAsString).withDefault([]),
    status: parseAsArrayOf(parseAsStringLiteral(STATUS_VALUES)).withDefault([]),
    owner: parseAsString,
  })

  function buildRequest(): RagQueryRequest {
    return {
      query: query.trim(),
      visibility: scope.vis as Visibility,
      use_hybrid: scope.hybrid,
      use_rerank: scope.rerank,
      tags: scope.tags.length ? scope.tags : undefined,
      status: scope.status.length ? (scope.status as Status[]) : undefined,
      owner: scope.owner ?? undefined,
    }
  }

  function submit() {
    if (!query.trim() || isPending) return
    onSubmitMessage(buildRequest())
    setQuery('')
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    submit()
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      submit()
    }
  }

  const scopeActive =
    scope.vis !== 'public' ||
    scope.hybrid ||
    scope.rerank ||
    scope.tags.length > 0 ||
    scope.status.length > 0 ||
    !!scope.owner

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-hairline bg-surface-0 px-4 py-3"
      aria-label="Chat composer"
    >
      {scopeActive && (
        <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-fg-muted">
          <span>Scope:</span>
          <span className="font-mono">
            {scope.vis}
            {scope.hybrid && ' · hybrid'}
            {scope.rerank && ' · rerank'}
            {scope.tags.length > 0 && ` · tags=${scope.tags.join(',')}`}
            {scope.status.length > 0 && ` · status=${scope.status.join(',')}`}
            {scope.owner && ` · owner=${scope.owner}`}
          </span>
        </div>
      )}
      <div className="flex items-end gap-2">
        <textarea
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isPending}
          placeholder="Ask the knowledge base anything…"
          aria-label="Chat query"
          className="w-full bg-surface-2 border border-hairline rounded-control px-3 py-2 text-sm text-fg placeholder:text-fg-subtle focus:border-accent focus:ring-1 focus:ring-accent/30 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed resize-none font-sans"
        />
        <div className="flex flex-col items-end gap-1 shrink-0">
          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={isPending || !query.trim()}
          >
            <Send size={14} />
            Ask
          </Button>
          <span className="text-[10px] text-fg-subtle font-mono">⌘+Enter</span>
        </div>
      </div>
    </form>
  )
}
