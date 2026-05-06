import { ReactNode } from 'react'
import { Tabs as RadixTabs } from 'radix-ui'

interface Tab {
  id: string
  label: ReactNode
}

interface TabsProps {
  tabs: Tab[]
  activeTab: string
  onTabChange: (id: string) => void
  children: ReactNode
}

export function Tabs({ tabs, activeTab, onTabChange, children }: TabsProps) {
  return (
    <RadixTabs.Root value={activeTab} onValueChange={onTabChange} className="flex flex-col h-full">
      <RadixTabs.List className="flex border-b border-hairline" aria-label="Source detail sections">
        {tabs.map((tab) => (
          <RadixTabs.Trigger
            key={tab.id}
            value={tab.id}
            className="px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer border-b-2 -mb-px text-fg-muted border-transparent hover:text-fg hover:border-hairline-strong data-[state=active]:text-accent data-[state=active]:border-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-surface-0"
          >
            {tab.label}
          </RadixTabs.Trigger>
        ))}
      </RadixTabs.List>
      <div className="flex-1 overflow-hidden">{children}</div>
    </RadixTabs.Root>
  )
}
