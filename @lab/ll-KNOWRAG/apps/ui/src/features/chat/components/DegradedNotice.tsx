import { useState } from 'react'
import { AlertTriangle, Check, Copy } from 'lucide-react'
import { SourceChip } from './SourceChip'
import type { DegradedDetail } from '../types'

interface DegradedNoticeProps {
  detail: DegradedDetail
}

const DOCKER_EXEC_RE = /docker exec\s[^\n]*?ollama pull\s+\S+/

function extractDockerCommand(message: string): string | null {
  const m = message.match(DOCKER_EXEC_RE)
  if (!m) return null
  // Backend appends a sentence-ending period after the model name; strip it.
  return m[0].replace(/\.$/, '')
}

export function DegradedNotice({ detail }: DegradedNoticeProps) {
  const [copied, setCopied] = useState(false)
  const command = extractDockerCommand(detail.message)

  async function handleCopy() {
    if (!command) return
    try {
      await navigator.clipboard.writeText(command)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      // best-effort
    }
  }

  return (
    <div
      role="alert"
      className="rounded-card border border-status-warn/40 bg-status-warn/10 p-3 text-sm text-status-warn"
    >
      <div className="flex items-start gap-2">
        <AlertTriangle size={16} className="mt-0.5 shrink-0" />
        <div className="flex-1 space-y-2">
          <p className="font-medium">
            {detail.error_code === 'chat_provider_unavailable'
              ? 'Chat provider unreachable'
              : 'Chat model unavailable'}
          </p>
          <p className="text-fg-muted text-xs leading-relaxed">{detail.message}</p>
          {command && (
            <div className="flex items-center gap-2 rounded-control border border-hairline bg-surface-2 px-2 py-1 font-mono text-xs text-fg">
              <code className="flex-1 break-all">{command}</code>
              <button
                type="button"
                onClick={handleCopy}
                aria-label={copied ? 'Copied' : 'Copy command'}
                className="inline-flex size-6 items-center justify-center rounded-control text-fg-muted hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent cursor-pointer"
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
              </button>
            </div>
          )}
        </div>
      </div>
      {detail.retrieved_context.length > 0 && (
        <div className="mt-3 pt-3 border-t border-status-warn/20">
          <p className="text-xs text-fg-muted mb-2">
            Retrieved context ({detail.retrieved_context.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {detail.retrieved_context.map((hit, i) => (
              <SourceChip key={`${hit.artifact_path}:${hit.chunk_index}`} hit={hit} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
