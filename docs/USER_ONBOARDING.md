# User Onboarding (Day 1 Guide)

Welcome to the W7-Base local orchestration platform. This guide will walk you through your first 15 minutes as an operator.

## Step 1: Shell Integration
Add the following to your shell profile (`~/.bashrc` or `~/.zshrc`):
```bash
source ~/w7-localbase/.shared/w7.sh
```
*Reload your shell.*

## Step 2: Secret Management Setup
1. **Install SOPS & AGE:**
   ```bash
   brew install sops age
   ```
2. **Generate your personal key:**
   ```bash
   age-keygen -o ~/.config/sops/age/keys.txt
   ```
3. **Configure SOPS:** Update the `public_key` in `.sops.yaml` with your new key's public ID.

## Step 3: Boot Infrastructure
Start the core platform services:
```bash
w7 up all
```
*Wait for Gitea, Traefik, and Webhook to report 'UP' in `w7 stat`.*

## Step 4: Access the UI
Configure your `/etc/hosts`:
```text
127.0.0.1 git.w7.local logs.w7.local webhook.w7.local whoami.w7.local
```
Visit `http://git.w7.local` and set up your admin account.

## Step 5: Your First Stack
1. **Initialize:** `w7 init @dev/hello-world`
2. **Configure:** Edit `compose.yml` and `.env.example`.
3. **Seal Secrets:** `w7 secret init @dev/hello-world`
4. **Deploy:** `w7 up hello-world`

## Step 6: Explore Observability
Visit `http://grafana.w7.local` (admin/admin) to view the global health dashboard.
