import { ReactNode } from 'react'
import { ViewTabs } from './ViewTabs'
import { HeaderStatusPill } from './HeaderStatusPill'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-col h-screen bg-surface-0">
      <header className="h-14 px-6 border-b border-hairline bg-surface-0 flex items-center justify-between shrink-0">
        <h1 className="text-lg font-semibold tracking-tight">KnowRAG</h1>
        <ViewTabs />
        <HeaderStatusPill />
      </header>
      <div className="flex-1 min-h-0">{children}</div>
    </div>
  )
}
