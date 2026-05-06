import { useState } from 'react'
import ReactMarkdown, { Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Check, Copy } from 'lucide-react'
import { cn } from '../../../lib/cn'

interface MarkdownViewProps {
  body: string
  className?: string
}

// react-markdown v10 removed the `className` prop — wrap externally.
export function MarkdownView({ body, className }: MarkdownViewProps) {
  return (
    <div className={cn('prose prose-invert max-w-none', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { detect: true, ignoreMissing: true }]]}
        components={MARKDOWN_COMPONENTS}
      >
        {body}
      </ReactMarkdown>
    </div>
  )
}

const MARKDOWN_COMPONENTS: Components = {
  a: ({ href, children, ...rest }) => {
    const isAnchor = typeof href === 'string' && href.startsWith('#')
    return (
      <a
        href={href}
        {...rest}
        {...(isAnchor
          ? {}
          : { target: '_blank', rel: 'noopener noreferrer nofollow ugc' })}
      >
        {children}
      </a>
    )
  },
  pre: ({ children, ...rest }) => <CodeBlock {...rest}>{children}</CodeBlock>,
}

function CodeBlock({ children }: { children?: React.ReactNode }) {
  const [copied, setCopied] = useState(false)
  // react-markdown nests <code> inside <pre>; extract the raw text.
  const codeChild = (children as any)?.props?.children
  const codeText = Array.isArray(codeChild) ? codeChild.join('') : String(codeChild ?? '')
  const language = (children as any)?.props?.className?.match(/language-([\w-]+)/)?.[1]

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(codeText)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      // best-effort
    }
  }

  return (
    <div className="not-prose group relative my-4">
      {language && (
        <span className="absolute top-2 left-3 text-[10px] uppercase tracking-wide text-fg-subtle font-mono pointer-events-none select-none">
          {language}
        </span>
      )}
      <button
        type="button"
        onClick={handleCopy}
        aria-label={copied ? 'Copied' : 'Copy code'}
        aria-live="polite"
        className="absolute top-2 right-2 size-7 inline-flex items-center justify-center rounded-control border border-hairline bg-surface-1/80 text-fg-muted hover:text-fg hover:border-hairline-strong opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
      >
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
      <pre className="bg-surface-2 border border-hairline rounded-card overflow-x-auto p-4 text-xs leading-relaxed">
        {children}
      </pre>
    </div>
  )
}
