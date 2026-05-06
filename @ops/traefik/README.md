# Traefik Stack (@ops/traefik)

The global reverse proxy and load balancer for the W7-Base platform. It handles all incoming traffic to `*.w7.local` and routes it to the appropriate Docker containers.

## Configuration
- **Entrypoints:**
  - HTTP: Port `80`
  - HTTPS: Port `443`
  - Dashboard: Port `8080` (Insecure mode enabled)
- **Provider:** Docker (Automated discovery of containers)
- **Network:** `w7-ingress`

## Features
- **Dynamic Configuration:** Automatically discovers new containers with `traefik.enable=true` labels.
- **W7 Integration:** Connected to the external `w7-ingress` network.
- **Monitoring:** Dashboard available at `http://localhost:8080`.

## Management
```bash
w7 up @ops/traefik
w7 logs @ops/traefik
w7 backup @ops/traefik
```

## Secret Management
No external secrets required for base configuration. For advanced HTTPS or DNS-01 challenges, add variables to `.env`.
