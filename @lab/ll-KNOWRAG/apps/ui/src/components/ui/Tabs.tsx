import { ReactNode, useState } from 'react'

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
    <div className="flex flex-col h-full">
      <div className="flex border-b border-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              px-4 py-2.5 text-sm font-medium transition-colors cursor-pointer
              border-b-2 -mb-px
              ${activeTab === tab.id
                ? 'text-accent border-accent'
                : 'text-text-secondary border-transparent hover:text-text-primary hover:border-border-active'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  )
}
