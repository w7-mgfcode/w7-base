import { HoverCard } from 'radix-ui'
import { parseAsString, parseAsStringLiteral, useQueryStates } from 'nuqs'
import { VIEW_VALUES } from '../../../shell/ViewTabs'
import type { RagQueryHit } from '../types'

interface SourceChipProps {
  hit: RagQueryHit
  index: number
}

export function SourceChip({ hit, index }: SourceChipProps) {
  const [, setNav] = useQueryStates({
    view: parseAsStringLiteral(VIEW_VALUES).withDefault('catalog'),
    a: parseAsString,
  })

  const basename = hit.artifact_path.split('/').pop() ?? hit.artifact_path
  const snippet = hit.content.slice(0, 180)

  return (
    <HoverCard.Root openDelay={200} closeDelay={80}>
      <HoverCard.Trigger asChild>
        <button
          type="button"
          onClick={() => setNav({ view: 'catalog', a: hit.artifact_path })}
          className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2 py-0.5 font-mono text-xs text-accent hover:bg-accent/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface-0 cursor-pointer"
          aria-label={`Open ${hit.artifact_path} in catalog`}
        >
          <span className="opacity-70">[{index}]</span>
          <span className="truncate max-w-[14rem]">{basename}</span>
        </button>
      </HoverCard.Trigger>
      <HoverCard.Portal>
        <HoverCard.Content
          side="top"
          align="start"
          sideOffset={6}
          className="z-50 max-w-sm rounded-card border border-hairline bg-surface-1 p-3 text-xs text-fg shadow-none"
        >
          <p className="font-mono text-fg break-all">{hit.artifact_path}</p>
          {hit.section_title && (
            <p className="mt-1 text-fg-muted">{hit.section_title}</p>
          )}
          {hit.tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {hit.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full border border-hairline px-1.5 py-0.5 text-[10px] text-fg-muted"
                >
                  {t}
                </span>
              ))}
            </div>
          )}
          <p className="mt-2 text-fg-muted leading-relaxed line-clamp-4">
            {snippet}
            {hit.content.length > snippet.length && '…'}
          </p>
          <HoverCard.Arrow className="fill-hairline" />
        </HoverCard.Content>
      </HoverCard.Portal>
    </HoverCard.Root>
  )
}
