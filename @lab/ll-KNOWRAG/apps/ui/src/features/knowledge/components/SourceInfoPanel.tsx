import { useState } from 'react'
import { Source } from '../types'
import { Input } from '../../../components/ui/Input'
import { Button } from '../../../components/ui/Button'
import { TagEditor } from './TagEditor'
import { useUpdateSource } from '../hooks/useKnowledgeQueries'
import { Copy, Check } from 'lucide-react'

interface SourceInfoPanelProps {
  source: Source
}

export function SourceInfoPanel({ source }: SourceInfoPanelProps) {
  const [title, setTitle] = useState(source.title || '')
  const [displayName, setDisplayName] = useState(source.source_display_name || '')
  const [tags, setTags] = useState<string[]>(source.metadata?.tags || [])
  const [copied, setCopied] = useState(false)
  const updateMutation = useUpdateSource()

  const hasChanges =
    title !== (source.title || '') ||
    displayName !== (source.source_display_name || '') ||
    JSON.stringify(tags) !== JSON.stringify(source.metadata?.tags || [])

  const handleSave = () => {
    updateMutation.mutate({
      sourceId: source.source_id,
      data: { title, display_name: displayName, tags },
    })
  }

  const handleCopy = () => {
    if (source.source_url) {
      navigator.clipboard.writeText(source.source_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="p-5 space-y-4">
      <div>
        <label className="block text-xs text-fg-muted mb-1">Title</label>
        <Input value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div>
        <label className="block text-xs text-fg-muted mb-1">Display Name</label>
        <Input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
      </div>
      <div>
        <label className="block text-xs text-fg-muted mb-1">Tags</label>
        <TagEditor tags={tags} onChange={setTags} />
      </div>
      <div>
        <label className="block text-xs text-fg-muted mb-1">Source URL</label>
        <div className="flex items-center gap-2">
          <span className="flex-1 text-sm font-mono text-fg-muted bg-surface-2 rounded-md px-3 py-2 truncate">
            {source.source_url || '—'}
          </span>
          {source.source_url && (
            <button onClick={handleCopy} className="text-fg-subtle hover:text-fg cursor-pointer">
              {copied ? <Check size={16} className="text-accent" /> : <Copy size={16} />}
            </button>
          )}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="block text-xs text-fg-muted">Created</span>
          <span className="text-fg">{new Date(source.created_at).toLocaleString()}</span>
        </div>
        <div>
          <span className="block text-xs text-fg-muted">Updated</span>
          <span className="text-fg">{new Date(source.updated_at).toLocaleString()}</span>
        </div>
      </div>
      {hasChanges && (
        <Button onClick={handleSave} disabled={updateMutation.isPending} size="sm">
          {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </Button>
      )}
    </div>
  )
}
