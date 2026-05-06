# @ops/act-runner

## Overview
The Act Runner provides a local, GitHub-compatible CI/CD execution engine for the Gitea instance.

## Configuration
- `compose.yml`: Defines the runner service.
- `config.yaml`: Core runner settings.
- `.env.example`: Template for instance URL and registration token.
- `data/`: Runner's state and history.

## Features
- **Gitea Actions**: Runs local workflows on push.
- **Docker in Docker**: Spawns isolated job containers.

## Management
```bash
w7 up @ops/act-runner
```

## Secret Management
Requires `GITEA_RUNNER_REGISTRATION_TOKEN` from the Gitea UI to be saved in the local `.env`.
