# Gitea Stack (@ops/gitea)

Local Gitea instance for hosting Git repositories, providing an OCI registry, and serving as the control plane for local CI/CD via Gitea Actions.

## Configuration
- **Domain:** `http://git.w7.local`
- **Internal Port:** `3000` (Traefik routed)
- **SSH Port:** `222` (Host mapped)
- **Database:** SQLite3 (Local)
- **Persistence:** `./data`

## Features
- **Actions Enabled:** Integrated support for Gitea Actions.
- **W7 Ingress:** Connected to the `w7-ingress` network for seamless reverse proxying.

## Management
```bash
w7 up @ops/gitea
w7 logs @ops/gitea
w7 backup @ops/gitea
```

## Secret Management
Requires `GITEA__database__PASS` in `.env`. Use `w7 secret init @ops/gitea` to seal secrets after initial setup.
