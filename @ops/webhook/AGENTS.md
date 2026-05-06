# Webhook Agent Instructions

## Context
This is the delivery heart of the W7-Base platform. It has root-level access to the host Docker daemon.

## Guidelines
- **Deploy Scripts:** All shell scripts in `./scripts` should be idempotent and use the unified `w7` CLI.
- **Rollback Policy:** Always perform a safety check (`docker compose config`) before updating running containers.
- **Gitea Integration:** When setting up a new repository, the webhook URL should be `http://webhook-listener:9000/hooks/deploy-w7` if using the internal Docker network.
