# Dogfood Report — PR #72 (Epic 2: Chat RAG-Q&A surface)

**Timestamp (UTC):** 2026-05-10T21:09:59Z
**Branch:** `feat/ui-chat-rag-surface`
**Closes:** #57 + sub-issues #67, #68, #69, #70, #71

## Verification mode

**No-screenshot.** `agent-browser` requires `--no-sandbox` on this Ubuntu 26
host (kernel disallows unprivileged user namespaces by default), and that
flag is gated by W7-Base's "Create Unsafe Agents" rule. Visual dogfood is
deferred to the operator; this report captures everything verifiable without
a live browser sandbox.

## Stack state

| Service | Status | Notes |
|---|---|---|
| knowrag-api | Up 2 h (healthy) | `GET /api/health → 200` |
| knowrag-ui | Up (just rebuilt with this PR's bundle) | `GET / → 200` |
| knowrag-gitea | Up 4 h (healthy) | KB repo seeded |
| knowrag-qdrant | Up 4 h (healthy) | embeddings present (3 hits returned) |
| knowrag-ollama | Up 4 h (healthy) | **only `nomic-embed-text` pulled — no chat model** — this is the natural trigger for the DegradedNotice path |
| knowrag-mcp | Up 4 h | not exercised in this dogfood |

## Bundle inspection — new chat surface symbols present in deployed JS

`/assets/index-DDyewNru.js` (671 KiB):

| Symbol | Hits | Source |
|---|---|---|
| `Ask the knowledge base anything` | 2 | `ChatView` empty-state title + description |
| `Sources (` | 1 | `ChatMessage` sources row label |
| `Retrieved context (` | 1 | `DegradedNotice` context label |
| `chat_provider_unavailable` | 2 | `ragService` discriminated-union code + `DegradedNotice` label switch |
| `chat_model_unavailable` | 1 | `DegradedNotice` label switch |
| `ollama pull` | 1 | `DegradedNotice` docker-exec extractor |
| `Thinking` | 1 | `ChatView` pending-spinner copy |
| `/api/rag/query` | 1 | `ragService.postRagQuery` |
| `⌘+Enter / Ctrl+Enter` | 3 | empty-state hint + composer micro-hint |

All chat surface symbols confirmed present in the bundle the production
container is serving. The Epic-5 (#60) grep target
`grep -q 'Ask the knowledge base'` against the deployed bundle returns 2 hits.

## Live contract validation

### `POST /api/rag/query` — DegradedNotice path

```
POST /api/rag/query → 503
```

`detail`:
- `error_code:      chat_model_unavailable`
- `message length:  183 chars`
- `has docker exec: True`
- `context hits:    3`
- `first hit path:  prompts/claude-agents-knowrag-investigator.md`

This matches the contract the UI's discriminated union consumes:

```ts
type RagQueryResult =
  | { ok: true; data: RagQueryResponse }
  | { ok: false; degraded: DegradedDetail }   // ← this branch on the live stack
  | { ok: false; error: Error }
```

When the operator types a query and presses `⌘+Enter`, the UI will render
`DegradedNotice` with:
- the warn-tinted banner + `Chat model unavailable` label,
- the actionable command `docker exec -it knowrag-ollama ollama pull llama3.2:1b` with a copy button,
- the 3 retrieved-context hits as `SourceChip`s, each clickable to navigate to `?view=catalog&a=<path>`.

Full 503 response saved in `rag-degraded-response.json` next to this report.

### UI nginx proxy — `/api/*` smoke (regression check from #51)

```
GET http://localhost:3737/api/health → 200
```

Catalog smoke from #51 still passes; the new ChatView shares the same proxy.

## What this report does NOT cover

- Visual screenshot of the chat tab empty state.
- Visual screenshot of the DegradedNotice with retrieved-context chips.
- Visual screenshot of a SourceChip click navigating to the cited artifact.
- The happy path (chat model pulled). Would require ~1.3 GB pull of `llama3.2:1b`.

Either authorize agent-browser with `--no-sandbox` (Ubuntu 26 kernel
constraint), or capture these manually with the local browser.

## Next step suggestions

1. `docker exec -it knowrag-ollama ollama pull llama3.2:1b` to also exercise the happy path.
2. Open `http://knowrag-ui.w7.local/?view=chat` in a real browser; submit a question; verify both the answer + source-chip flow and the degraded path (re-stop the chat model after pull).
3. Save real screenshots into this same directory.
