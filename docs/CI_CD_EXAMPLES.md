# CI/CD Workflow Examples

W7-Base uses Gitea Actions (`act-runner`) for automated pipelines. This document provides standardized GitHub Actions-compatible workflow examples for your local stacks.

## 1. Basic Build & Test (Any Language)
Place this in `.github/workflows/test.yaml` within your repository.

```yaml
name: Test Suite
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          echo "Running local tests..."
          # Insert your test commands here
```

## 2. Docker Image Build & Push to Gitea Registry
Configure this workflow to build images and push them to the internal Gitea registry.

```yaml
name: Docker Build & Push
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Login to Gitea Registry
        run: echo "${{ secrets.GITEA_TOKEN }}" | docker login git.w7.local:3000 -u ${{ github.actor }} --password-stdin
      - name: Build and Push
        run: |
          docker build -t git.w7.local:3000/${{ github.repository }}:latest .
          docker push git.w7.local:3000/${{ github.repository }}:latest
```

## 3. High-Trust Deployment (Self-Hosted Runner)
For stacks in `@prod` or `@ops`, use a self-hosted runner to execute `w7` CLI commands directly on the host machine.

```yaml
name: Direct Host Deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: self-hosted  # Use the w7-local-runner
    steps:
      - uses: actions/checkout@v3
      - name: Run W7 Deploy
        run: |
          # The runner has access to the w7 bridge
          w7 up ${{ github.repository }} --yes
```

## 4. Hybrid Sync (Webhook + Pipeline)
For most `@dev` stacks, combine a Webhook for instant sync and a pipeline for testing:
1. **Webhook:** Set in Gitea Repo Settings -> Webhooks. Points to `http://webhook.w7.local`.
2. **Pipeline:** Runs on every push to ensure code quality before the auto-sync triggers the deployment.
