import { parseAsStringLiteral, useQueryState } from 'nuqs'
import { AppShell } from './shell/AppShell'
import { VIEW_VALUES } from './shell/ViewTabs'
import { CatalogView } from './features/catalog/views/CatalogView'
import { EmptyState } from './components/ui/EmptyState'

function Placeholder({ name }: { name: string }) {
  return (
    <div className="flex flex-col h-full">
      <main className="flex-1 overflow-y-auto p-4">
        <EmptyState
          title={`${name} — coming soon`}
          description={`The ${name.toLowerCase()} surface lands in a follow-up sub-issue.`}
        />
      </main>
    </div>
  )
}

function App() {
  const [view] = useQueryState(
    'view',
    parseAsStringLiteral(VIEW_VALUES).withDefault('catalog'),
  )
  return (
    <AppShell>
      {view === 'chat' ? (
        <Placeholder name="Chat" />
      ) : view === 'operator' ? (
        <Placeholder name="Operator" />
      ) : (
        <CatalogView />
      )}
    </AppShell>
  )
}

export default App
