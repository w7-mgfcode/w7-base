# @ops/w7-exporter

## Overview
The W7 Exporter is a custom platform bridge that transforms W7 CLI data (`w7 stat`, `w7 doctor`) into Prometheus-readable metrics.

## Configuration
- `compose.yml`: Defines the exporter service.
- `exporter.py`: The Python script that runs the metrics server.

## Features
- **Platform Health**: Exports global health and container counts.
- **Docker Integration**: Directly interacts with the Docker socket.

## Management
```bash
w7 up @ops/w7-exporter
```

## Secret Management
No secrets.
