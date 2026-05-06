# Observability Deep-Dive

This document details the monitoring, logging, and metrics architecture of the W7-Base platform.

## 1. Monitoring Stack (@ops)
The observability layer is powered by the Prometheus ecosystem:
- **Prometheus** (`@ops/prometheus`): The central metrics engine.
- **Grafana** (`@ops/grafana`): Visualization and alerting dashboard.
- **Node Exporter** (`@ops/node-exporter`): Host-level hardware metrics.
- **W7 Exporter** (`@ops/w7-exporter`): A custom bridge transforming `w7 doctor` and `w7 stat` into Prometheus metrics.

## 2. Platform Health Metrics
The `w7-exporter` provides unique metrics for local orchestration:
- `w7_healthy`: Global system status (1 = Healthy, 0 = Unhealthy).
- `w7_error_count` / `w7_warning_count`: Totals from the latest `doctor` run.
- `w7_containers_up{zone="..."}`: Real-time container counts per deployment zone.
- `w7_policy_violation{zone="...", stack="...", policy="..."}`: Tracks policy failures.

## 3. Logging Strategy
W7-Base utilizes **Dozzle** (`@ops/dozzle`) for real-time log streaming.
- **URL:** `http://logs.w7.local`
- **Native Logs:** Use `w7 logs <stack>` for CLI-based tailing with ANSI colors.
- **Retention:** By default, Docker logs are managed by the host's log-driver settings.

## 4. Custom Metrics for Stacks
To add metrics for your own application:
1. Ensure your application exposes a `/metrics` endpoint (Prometheus format).
2. Add your service as a target in `@ops/prometheus/config/prometheus.yml`:
   ```yaml
   - job_name: 'my-app'
     static_configs:
       - targets: ['my-app-server:8080']
   ```
3. Restart Prometheus: `w7 up @ops/prometheus`.

## 5. Grafana Dashboard Provisioning
Dashboards are stored as JSON in `@ops/grafana/provisioning/dashboards`. 
- **W7 Global Health:** UID `w7-global-health`.
- **Custom Dashboards:** Add your JSON files to the provisioning directory to automatically load them on startup.

## 6. Alerting
Prometheus Alertmanager is configured in `@ops/prometheus/config/alerting.yml`. 
- **Default Alerts:** Trigger if `w7_healthy == 0` for > 1 minute.
- **Custom Alerts:** Define new rules based on application-specific metrics.
