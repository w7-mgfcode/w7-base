import { Tabs } from 'radix-ui'
import { parseAsStringLiteral, useQueryState } from 'nuqs'

export const VIEW_VALUES = ['catalog', 'chat', 'operator'] as const
export type ViewValue = (typeof VIEW_VALUES)[number]

const TRIGGERS: { value: ViewValue; label: string }[] = [
  { value: 'catalog', label: 'Catalog' },
  { value: 'chat', label: 'Chat' },
  { value: 'operator', label: 'Operator' },
]

export function ViewTabs() {
  const [view, setView] = useQueryState(
    'view',
    parseAsStringLiteral(VIEW_VALUES).withDefault('catalog'),
  )

  return (
    <Tabs.Root value={view} onValueChange={(v) => setView(v as ViewValue)}>
      <Tabs.List
        aria-label="KnowRAG views"
        className="flex"
      >
        {TRIGGERS.map((t) => (
          <Tabs.Trigger
            key={t.value}
            value={t.value}
            className="px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer border-b-2 -mb-px text-fg-muted border-transparent hover:text-fg hover:border-hairline-strong data-[state=active]:text-accent data-[state=active]:border-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface-0"
          >
            {t.label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>
    </Tabs.Root>
  )
}
