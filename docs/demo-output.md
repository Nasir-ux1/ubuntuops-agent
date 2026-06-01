# Demo Output

Saved service-log analysis:

```bash
PYTHONPATH=src python -m ubuntuops.cli service nginx --journal-file samples/journal_nginx_failed.log
```

Expected output:

```text
[HIGH] Port already in use: nginx logs match a known failure pattern: Port already in use.
[MEDIUM] Restart loop: nginx logs match a known failure pattern: Restart loop.
[MEDIUM] Configuration error: nginx logs match a known failure pattern: Configuration error.
```

SSH/auth-log analysis:

```bash
PYTHONPATH=src python -m ubuntuops.cli diagnose --issue "ssh login attempts are high" --auth-log samples/auth.log
```

Expected output:

```text
Top finding: Failed SSH login attempts detected (medium). 4 failed SSH attempts found; top source is 203.0.113.10 with 3.
Report written to: reports/incident_report.md
```
