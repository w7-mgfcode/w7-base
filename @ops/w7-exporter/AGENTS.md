# Agent Context: @ops/w7-exporter

## Context
Bridge between the shell-based W7 CLI and the metrics ecosystem. Uses `w7` binary inside the container.

## Guidelines
- Ensure the `w7` binary and `.shared/` scripts are correctly mounted.
- If new CLI metrics are added, update `exporter.py`.
