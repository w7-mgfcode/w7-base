import { useState, useRef } from 'react'
import { CrawlMode } from '../types'
import { useStartCrawl, useUploadDocument } from '../hooks/useKnowledgeQueries'
import { Dialog } from '../../../components/ui/Dialog'
import { Input } from '../../../components/ui/Input'
import { Button } from '../../../components/ui/Button'
import { TagEditor } from './TagEditor'
import { CrawlModeSelector } from './CrawlModeSelector'
import { Upload } from 'lucide-react'

interface Props {
  onClose: () => void
  onSuccess: (result?: { crawlId?: string; sourceId?: string }) => void
}

export function AddKnowledgeDialog({ onClose, onSuccess }: Props) {
  const [tab, setTab] = useState<'crawl' | 'upload'>('crawl')

  // Crawl state
  const [url, setUrl] = useState('')
  const [crawlMode, setCrawlMode] = useState<CrawlMode>('discovery_auto')
  const [maxDepth, setMaxDepth] = useState(3)
  const [maxPages, setMaxPages] = useState(100)
  const [tags, setTags] = useState<string[]>([])
  const [crawlError, setCrawlError] = useState<string | null>(null)
  const startCrawl = useStartCrawl()

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadTags, setUploadTags] = useState<string[]>([])
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const uploadMutation = useUploadDocument()

  const handleCrawl = async () => {
    if (!url.trim()) return
    setCrawlError(null)
    try {
      const result = await startCrawl.mutateAsync({
        url,
        maxDepth: crawlMode === 'recursive' ? maxDepth : undefined,
        maxPages,
        tags: tags.length > 0 ? tags : undefined,
        mode: crawlMode,
      })
      onSuccess({ crawlId: result.crawl_id })
      onClose()
    } catch (err: any) {
      setCrawlError(err.message)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploadError(null)
    try {
      const tagStr = uploadTags.join(',')
      const result = await uploadMutation.mutateAsync({ file: selectedFile, tags: tagStr || undefined })
      onSuccess({ sourceId: result.source_id })
      onClose()
    } catch (err: any) {
      setUploadError(err.message)
    }
  }

  const isSubmitting = startCrawl.isPending || uploadMutation.isPending

  return (
    <Dialog
      open
      onClose={onClose}
      title="Add Knowledge"
      maxWidth="max-w-xl"
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
          <Button
            onClick={tab === 'crawl' ? handleCrawl : handleUpload}
            disabled={isSubmitting || (tab === 'crawl' ? !url.trim() : !selectedFile)}
          >
            {isSubmitting
              ? (tab === 'crawl' ? 'Starting...' : 'Uploading...')
              : (tab === 'crawl' ? 'Start Crawl' : 'Upload')
            }
          </Button>
        </>
      }
    >
      {/* Tab bar */}
      <div className="flex border-b border-border -mx-6 px-6 mb-4">
        <button
          onClick={() => setTab('crawl')}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px cursor-pointer ${
            tab === 'crawl' ? 'text-accent border-accent' : 'text-text-secondary border-transparent'
          }`}
        >
          Crawl Website
        </button>
        <button
          onClick={() => setTab('upload')}
          className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px cursor-pointer ${
            tab === 'upload' ? 'text-accent border-accent' : 'text-text-secondary border-transparent'
          }`}
        >
          Upload Document
        </button>
      </div>

      {tab === 'crawl' ? (
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-text-secondary mb-1">URL</label>
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://docs.example.com"
              autoFocus
            />
          </div>
          <div>
            <label className="block text-xs text-text-secondary mb-1">Crawl Mode</label>
            <CrawlModeSelector value={crawlMode} onChange={setCrawlMode} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {crawlMode === 'recursive' && (
              <div>
                <label className="block text-xs text-text-secondary mb-1">Max Depth</label>
                <Input type="number" min={1} max={10} value={maxDepth} onChange={(e) => setMaxDepth(Number(e.target.value))} />
              </div>
            )}
            <div>
              <label className="block text-xs text-text-secondary mb-1">Max Pages</label>
              <Input type="number" min={1} max={500} value={maxPages} onChange={(e) => setMaxPages(Number(e.target.value))} />
            </div>
          </div>
          <div>
            <label className="block text-xs text-text-secondary mb-1">Tags</label>
            <TagEditor tags={tags} onChange={setTags} />
          </div>
          {crawlError && <p className="text-sm text-error">{crawlError}</p>}
        </div>
      ) : (
        <div className="space-y-4">
          <div
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragging(false); const f = e.dataTransfer.files[0]; if (f) setSelectedFile(f) }}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragging ? 'border-accent bg-accent-muted' : 'border-border hover:border-border-active'
            }`}
          >
            <Upload size={24} className="mx-auto mb-2 text-text-tertiary" />
            <p className="text-sm text-text-secondary">
              {selectedFile ? selectedFile.name : 'Click or drag a file here'}
            </p>
            <p className="text-xs text-text-tertiary mt-1">HTML, TXT, MD</p>
            <input
              ref={fileRef}
              type="file"
              accept=".html,.txt,.md"
              className="hidden"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <div>
            <label className="block text-xs text-text-secondary mb-1">Tags</label>
            <TagEditor tags={uploadTags} onChange={setUploadTags} />
          </div>
          {uploadError && <p className="text-sm text-error">{uploadError}</p>}
        </div>
      )}
    </Dialog>
  )
}
