# Webhook Stack (@ops/webhook)

The W7-Base GitOps deployment engine. This stack listens for local Gitea webhooks and triggers automated deployments based on stack-level metadata.

## Configuration
- **Domain:** `http://webhook.w7.local`
- **Internal Port:** `9000` (Traefik routed)
- **Hooks Config:** `./hooks.json`
- **Scripts Dir:** `./scripts`
- **Isolation Network:** `w7-ingress`

## Features
- **GitOps Engine:** Orchestrates automated `git pull` and `w7 up` cycles.
- **HMAC Signature Check:** Validates all incoming payloads via `WEBHOOK_SECRET`.
- **Pre-Deploy Validation:** Automatically rolls back on `docker compose config` failure.

## Management
```bash
w7 up @ops/webhook
w7 logs @ops/webhook
w7 backup @ops/webhook
```

## Secret Management
Requires `WEBHOOK_SECRET` in `.env`. This MUST match the secret configured in your Gitea repository settings.
