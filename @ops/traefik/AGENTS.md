# Traefik Agent Instructions

## Context
This is the core ingress controller. Misconfiguration here can take down all `*.w7.local` services.

## Guidelines
- **Routing Changes:** When adding new routes, verify the host rule and service port in the target stack's `compose.yml`.
- **Labels:** Ensure all proxied containers have the `traefik.enable=true` label and are attached to the `w7-ingress` network.
- **Safety:** Do not expose the Docker socket (`/var/run/docker.sock`) beyond the proxy container.
