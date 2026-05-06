# Gitea Agent Instructions

## Context
This is a local Gitea instance. It is the Source of Truth for the W7-Base GitOps flow.

## Guidelines
- **Workflow Changes:** When modifying Actions or Webhooks, ensure they are reflected in the global `.shared/GITOPS_DESIGN.md`.
- **User Management:** Prefer keeping the admin user local and not exposing it to the public internet.
- **Repository Layout:** Stacks managed by W7 should ideally have their own repositories in this Gitea instance to enable automated sync via the `@ops/webhook` stack.
