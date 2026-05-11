import { Card } from '../../../components/ui/Card'
import { HealthCard } from '../components/HealthCard'
import { ReconcileButton } from '../components/ReconcileButton'
import { SettingsPanel } from '../components/SettingsPanel'

export function OperatorView() {
  return (
    <div className="flex flex-col h-full">
      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto space-y-4">
          <HealthCard />
          <Card>
            <header className="mb-3">
              <h2 className="text-sm font-semibold text-fg">Reconcile</h2>
              <p className="mt-1 text-xs text-fg-muted">
                Walk the Gitea KB repo and re-embed any artifact whose hash
                diverged from the Qdrant index. Safe to run — but invalidates
                the catalog and search caches on success.
              </p>
            </header>
            <ReconcileButton />
          </Card>
          <SettingsPanel />
        </div>
      </main>
    </div>
  )
}
