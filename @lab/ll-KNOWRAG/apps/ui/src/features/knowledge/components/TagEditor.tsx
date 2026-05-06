import { useState, KeyboardEvent } from 'react'
import { X } from 'lucide-react'
import { Badge } from '../../../components/ui/Badge'

interface TagEditorProps {
  tags: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
}

export function TagEditor({ tags, onChange, placeholder = 'Add tag...' }: TagEditorProps) {
  const [input, setInput] = useState('')

  const addTag = () => {
    const tag = input.trim().toLowerCase()
    if (tag && !tags.includes(tag)) {
      onChange([...tags, tag])
    }
    setInput('')
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    } else if (e.key === 'Backspace' && !input && tags.length > 0) {
      onChange(tags.slice(0, -1))
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5 bg-surface-2 border border-hairline rounded-md px-2 py-1.5 min-h-[36px]
      focus-within:border-accent focus-within:ring-1 focus-within:ring-accent/30">
      {tags.map((tag) => (
        <Badge key={tag} variant="accent" className="gap-1">
          {tag}
          <button
            onClick={() => onChange(tags.filter((t) => t !== tag))}
            className="hover:text-fg cursor-pointer"
          >
            <X size={12} />
          </button>
        </Badge>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={addTag}
        placeholder={tags.length === 0 ? placeholder : ''}
        className="flex-1 min-w-[60px] bg-transparent border-none outline-none text-sm text-fg placeholder:text-fg-subtle"
      />
    </div>
  )
}
