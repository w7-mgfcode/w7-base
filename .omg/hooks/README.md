# OmG Hooks

This directory contains the hook configuration and plugins for the OmG extension.

## Plugin Contract

Runtime adapters must implement the following contract:

```javascript
onHookEvent(event, sdk)
```

### `event` Envelope
- `event`: The name of the event triggered.
- `source`: The origin of the event.
- `session_id`: Unique identifier for the current session.
- `task_id`: Identifier for the current task.
- `lane`: The hook lane being executed (e.g., `P0-safety`).
- `subagent`: The subagent executing the hook (if applicable).
- `termination_reason`: Reason for termination (if a terminal event).
- `metadata`: Additional contextual data.

### `sdk` Capabilities
- `log(message)`: Log a message to the system.
- `state.get(key)`: Retrieve state.
- `state.set(key, value)`: Persist state.
- Optional runtime bridge methods depending on the execution environment.

## Default Guardrails
- Side-effect hooks are disabled for delegated worker sessions unless explicitly opted in.
- Non-critical lanes (e.g., `P2-optimization`) are fail-open.
- Explicit safety violations (e.g., `P0-safety`) are fail-closed.
- Blocked continuations must re-enter the safety lane before proceeding to quality or optimization lanes.
- Terminal hook outcomes are recorded exactly once per agent turn.
- Persisted hook state should avoid timestamps or volatile churn unless operator-visible.