# UbuntuOps Runbook

Use this runbook when a Linux host reports service failures, login anomalies, or disk pressure.

## Service Down

1. Run `ubuntuops service <name>`.
2. Check for known patterns: port conflict, permission denied, missing file, restart loop, config error.
3. Validate the first error in `journalctl`, not only the final systemd failure line.
4. Apply the recommended fix and restart the service.

## Disk Full

1. Run `ubuntuops disk --path /`.
2. Check highest filesystem usage.
3. Inspect largest top-level directories.
4. Look for deleted-but-open files with `lsof +L1`.
5. Review Docker disk usage before pruning.

## SSH Brute Force

1. Run `ubuntuops ssh --log /var/log/auth.log`.
2. Review top failed-login source IPs.
3. Confirm successful logins are expected.
4. Enable fail2ban and disable password authentication where possible.
