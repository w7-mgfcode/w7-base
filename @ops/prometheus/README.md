# @ops/prometheus

## Overview
Prometheus is the core monitoring hub for the W7-Base framework. It scrapes metrics from various exporters and platform services.

## Configuration
- `compose.yml`: Defines the Prometheus service.
- `config/prometheus.yml`: Scrape configurations and global settings.
- `config/rules.yml`: Alerting and recording rules.
- `data/`: Persistent storage for time-series data.

## Features
- **Scraping**: Collects metrics from nodes and platform exporters.
- **Alerting**: Rule-based alerting via `rules.yml`.
- **UI**: Accessible at `http://prom.w7.local` via Traefik.

## Management
```bash
w7 up @ops/prometheus
w7 logs @ops/prometheus
```

## Secret Management
No significant secrets; environment variables in `.env` if necessary.
