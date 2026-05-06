# Agent Context: @ops/act-runner

## Context
Execution worker for CI/CD jobs. Connects to `gitea-server` over the internal Docker network.

## Guidelines
- Requires manual token registration on first setup.
- Monitor the `/var/run/docker.sock` usage for potential security risks.
- Check `w7 logs @ops/act-runner` if jobs are not starting.
