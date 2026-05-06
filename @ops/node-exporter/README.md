# @ops/node-exporter

## Overview
Node Exporter provides host-level metrics for the W7-Base framework. It runs as a sidecar to expose OS-level hardware and performance data.

## Configuration
- `compose.yml`: Defines the Node Exporter service.

## Features
- **Host Metrics**: CPU, memory, disk, and network stats.
- **Root FS Access**: Mounted root to gather filesystem usage.

## Management
```bash
w7 up @ops/node-exporter
```

## Secret Management
No secrets; purely metrics data.
