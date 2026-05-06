import { useState } from 'react'
import { Page } from '../types'
import { Copy, Check } from 'lucide-react'

interface PageViewerProps {
  page: Page
}

export function PageViewer({ page }: PageViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(page.full_content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="mx-5 mb-4 bg-surface-2 rounded-lg border border-hairline">
      <div className="flex items-center justify-between px-4 py-2 border-b border-hairline">
        <div className="flex gap-4 text-xs text-fg-muted">
          <span>{page.word_count.toLocaleString()} words</span>
          <span>{page.char_count.toLocaleString()} chars</span>
        </div>
        <button onClick={handleCopy} className="text-fg-subtle hover:text-fg cursor-pointer">
          {copied ? <Check size={14} className="text-accent" /> : <Copy size={14} />}
        </button>
      </div>
      <pre className="px-4 py-3 text-xs text-fg whitespace-pre-wrap font-mono max-h-[400px] overflow-y-auto leading-relaxed">
        {page.full_content}
      </pre>
    </div>
  )
}
