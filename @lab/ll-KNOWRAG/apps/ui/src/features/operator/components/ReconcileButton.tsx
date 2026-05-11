import { AlertDialog } from 'radix-ui'
import { Button } from '../../../components/ui/Button'
import { Spinner } from '../../../components/ui/Spinner'
import { cn } from '../../../lib/cn'
import { useReconcileMutation } from '../hooks/useOperatorQueries'

export function ReconcileButton() {
  const mutation = useReconcileMutation()

  return (
    <div className="space-y-3">
      <AlertDialog.Root>
        <AlertDialog.Trigger asChild>
          <Button variant="secondary" disabled={mutation.isPending}>
            Reconcile Git ↔ Qdrant
          </Button>
        </AlertDialog.Trigger>
        <AlertDialog.Portal>
          <AlertDialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
          <AlertDialog.Content
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[min(90vw,28rem)] rounded-lg border border-hairline bg-surface-1 p-6 shadow-xl focus:outline-none"
          >
            <AlertDialog.Title className="text-base font-semibold text-fg">
              Run reconcile?
            </AlertDialog.Title>
            <AlertDialog.Description className="mt-2 text-sm text-fg-muted">
              This re-walks the Gitea KB repo and re-embeds any artifact whose
              hash diverged from the Qdrant index. Safe to run, but it can
              take a while on a large KB and will invalidate cached catalog
              and search results.
            </AlertDialog.Description>
            <div className="mt-5 flex items-center justify-end gap-2">
              <AlertDialog.Cancel asChild>
                <Button variant="ghost">Cancel</Button>
              </AlertDialog.Cancel>
              <AlertDialog.Action asChild>
                <Button
                  variant="primary"
                  disabled={mutation.isPending}
                  onClick={() => mutation.mutate()}
                >
                  {mutation.isPending ? <Spinner size={16} /> : null}
                  Confirm reconcile
                </Button>
              </AlertDialog.Action>
            </div>
          </AlertDialog.Content>
        </AlertDialog.Portal>
      </AlertDialog.Root>

      {mutation.isSuccess ? (
        <div
          role="status"
          className={cn(
            'rounded-md px-3 py-2 text-xs',
            'bg-status-ok/10 text-status-ok',
          )}
        >
          Reconcile complete — scanned {mutation.data.scanned} artifact
          {mutation.data.scanned === 1 ? '' : 's'}.
        </div>
      ) : null}

      {mutation.isError ? (
        <div
          role="alert"
          className={cn(
            'rounded-md px-3 py-2 text-xs',
            'bg-status-err/10 text-status-err',
          )}
        >
          Reconcile failed — {mutation.error.message}
        </div>
      ) : null}
    </div>
  )
}
