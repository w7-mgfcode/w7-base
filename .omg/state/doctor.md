# OmG Doctor Diagnostics

**Scope:** lane:ops | check:network

## Doctor Result
**Status:** Healthy (Internal) / DNS-Blocked (LAN)

## Findings
| Check | Status | Details |
|---|---|---|
| Extension Surface Integrity | 🟢 Pass | All required OmG directories and manifest files are intact. |
| Core Flow Commands | 🟢 Pass | `omg:*` commands are available and responsive. |
| Gitea Service Status | 🟢 Pass | `ops-server` is UP and responding at `172.21.0.11:3000`. |
| Traefik Routing | 🟢 Pass | Local routing for `git.w7.local` via `localhost:80` is functional (200 OK). |
| Host IP (LAN) | 🟡 Warn | Host reachable at `10.0.0.118` and `10.0.0.226`. |
| DNS Resolution (LAN) | 🔴 Fail | LAN devices cannot resolve `*.w7.local` without manual `/etc/hosts` or local DNS server. |
| Ingress Network | 🟢 Pass | `w7-ingress` bridge is healthy with 11 active containers. |

## Remediation Actions
1. **DNS Provisioning**: Deploy `dnsmasq` or similar to `@ops` to provide `*.w7.local` resolution for the LAN.
2. **mDNS/Avahi**: Enable Avahi-daemon on the host to broadcast `.local` records if applicable.
3. **Lane Cleanup**: Audit and track `@lab/Mannos-sos/` to restore `lab` lane health.

**Recommended Next Command:**
`/omg:plan --intent="Deploy local DNS for w7.local LAN resolution"`