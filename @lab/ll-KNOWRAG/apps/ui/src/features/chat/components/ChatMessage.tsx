import { MarkdownView } from '../../catalog/components/MarkdownView'
import { SourceChip } from './SourceChip'
import { DegradedNotice } from './DegradedNotice'
import type { ChatMessage as ChatMessageType } from '../types'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-surface-2 rounded-card px-4 py-3 max-w-[70%] text-fg whitespace-pre-wrap">
          {message.query}
        </div>
      </div>
    )
  }

  // assistant
  return (
    <div className="flex justify-start">
      <div className="bg-surface-1 rounded-card px-4 py-3 max-w-[80%] border border-hairline">
        {message.degraded ? (
          <DegradedNotice detail={message.degraded} />
        ) : (
          <>
            {message.answer && <MarkdownView body={message.answer} />}
            {message.hits && message.hits.length > 0 && (
              <div className="mt-3 pt-3 border-t border-hairline">
                <p className="text-xs text-fg-muted mb-2">
                  Sources ({message.hits.length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {message.hits.map((hit, i) => (
                    <SourceChip
                      key={`${hit.artifact_path}:${hit.chunk_index}`}
                      hit={hit}
                      index={i + 1}
                    />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
