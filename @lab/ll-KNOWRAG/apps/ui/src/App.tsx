import { parseAsStringLiteral, useQueryState } from 'nuqs'
import { AppShell } from './shell/AppShell'
import { VIEW_VALUES } from './shell/ViewTabs'
import { CatalogView } from './features/catalog/views/CatalogView'
import { ChatView } from './features/chat/views/ChatView'
import { OperatorView } from './features/operator/views/OperatorView'

function App() {
  const [view] = useQueryState(
    'view',
    parseAsStringLiteral(VIEW_VALUES).withDefault('catalog'),
  )
  return (
    <AppShell>
      {view === 'chat' ? (
        <ChatView />
      ) : view === 'operator' ? (
        <OperatorView />
      ) : (
        <CatalogView />
      )}
    </AppShell>
  )
}

export default App
