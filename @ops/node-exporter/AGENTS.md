# Agent Context: @ops/node-exporter

## Context
Exposes machine-level metrics to Prometheus. Used by Grafana dashboards for host health.

## Guidelines
- Do not restrict volume mounts unless required for security.
- Ensure the service is always available on the `w7-ingress` network.
