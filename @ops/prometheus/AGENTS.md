# Agent Context: @ops/prometheus

## Context
Prometheus acts as the central time-series database. It depends on other exporters like `node-exporter` and `w7-exporter`.

## Guidelines
- To add a new service for monitoring, update the `config/prometheus.yml` targets.
- Ensure all metric exporters are connected to the `w7-ingress` network for Prometheus to reach them.
- Monitor storage usage in the `data/` directory.
