# Network Topology & Architecture Diagram

This document provides a text-based representation of the W7-Base local network and service architecture.

## 1. Platform Topology

```mermaid
graph TD
    User([User/Operator]) -- Browser/CLI --> Traefik[@ops/traefik Proxy]
    
    subgraph Host Network
        Traefik -- Port 80/443 --> Ingress[w7-ingress Docker Network]
    end

    subgraph w7-ingress (Isolated Bridge)
        Ingress --> Gitea[@ops/gitea]
        Ingress --> Webhook[@ops/webhook]
        Ingress --> Monitoring[@ops/prometheus + @ops/grafana]
        Ingress --> Stacks[@dev / @prod / @lab stacks]
    end

    subgraph Control Plane Flow
        Gitea -- Webhook Event --> Webhook
        Webhook -- Git Pull/W7 Up --> Stacks
        ActRunner[@ops/act-runner] -- Docker Socket --> Stacks
    end

    subgraph Observability Flow
        Monitoring -- Scraping --> Stacks
        W7Exporter[@ops/w7-exporter] -- CLI Exec --> Monitoring
    end
```

## 2. Request Flow (External to Container)
1. **User** requests `http://git.w7.local`.
2. **DNS** (local `/etc/hosts`) resolves `git.w7.local` to `127.0.0.1`.
3. **Traefik** receives the request on host port `80`.
4. **Traefik Labels** match the `Host` header to the `gitea-server` container.
5. **Request** is routed over the `w7-ingress` internal network to the Gitea container on port `3000`.

## 3. Deployment Flow (GitOps)
1. **User** pushes to a local repository in Gitea.
2. **Gitea** fires a POST request to `webhook.w7.local/hooks/deploy-w7`.
3. **Webhook Listener** validates the HMAC signature.
4. **Listener** executes a deployment script:
   - `git pull` updates the local stack files on the host filesystem.
   - `w7 up <stack>` redeploys the containers.

## 4. Isolation Policy
Each zone (`@dev`, `@prod`, etc.) uses the same `w7-ingress` network for routing but is isolated at the **Compose Project Name** level (`<zone>-<stack>`). This prevents container name collisions while allowing the shared Traefik proxy to discover services across all zones.
