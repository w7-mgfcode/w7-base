import { CrawlMode } from '../types'
import { Badge } from '../../../components/ui/Badge'
import { Compass, FileText, Map, GitBranch } from 'lucide-react'

interface CrawlModeSelectorProps {
  value: CrawlMode
  onChange: (mode: CrawlMode) => void
}

const modes: { id: CrawlMode; label: string; desc: string; icon: typeof Compass; recommended?: boolean }[] = [
  { id: 'discovery_auto', label: 'Auto-detect', desc: 'llms.txt, sitemap, then recursive', icon: Compass, recommended: true },
  { id: 'single_page', label: 'Single page', desc: 'Crawl only the given URL', icon: FileText },
  { id: 'sitemap', label: 'Sitemap', desc: 'Follow sitemap.xml', icon: Map },
  { id: 'recursive', label: 'Recursive', desc: 'Follow all internal links', icon: GitBranch },
]

export function CrawlModeSelector({ value, onChange }: CrawlModeSelectorProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      {modes.map((m) => {
        const Icon = m.icon
        const selected = value === m.id
        return (
          <button
            key={m.id}
            type="button"
            onClick={() => onChange(m.id)}
            className={`
              flex flex-col items-start gap-1 p-3 rounded-lg border text-left cursor-pointer transition-colors
              ${selected
                ? 'border-accent bg-accent/5 text-text-primary'
                : 'border-border bg-bg-tertiary text-text-secondary hover:border-border-active'
              }
            `}
          >
            <div className="flex items-center gap-2">
              <Icon size={14} className={selected ? 'text-accent' : ''} />
              <span className="text-sm font-medium">{m.label}</span>
              {m.recommended && <Badge variant="accent">recommended</Badge>}
            </div>
            <span className="text-xs text-text-tertiary">{m.desc}</span>
          </button>
        )
      })}
    </div>
  )
}
