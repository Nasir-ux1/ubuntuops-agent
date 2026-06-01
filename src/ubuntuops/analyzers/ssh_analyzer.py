from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from ubuntuops.models import Finding


FAILED_RE = re.compile(r"Failed password .* from (?P<ip>\d+\.\d+\.\d+\.\d+)", re.I)
ACCEPTED_RE = re.compile(r"Accepted .* for (?P<user>[\w.-]+) from (?P<ip>\d+\.\d+\.\d+\.\d+)", re.I)
SUDO_RE = re.compile(r"sudo: .*COMMAND=(?P<command>.+)$", re.I)


def analyze_auth_log(path: str) -> list[Finding]:
    log_path = Path(path)
    if not log_path.exists():
        return [
            Finding(
                title="Auth log not found",
                severity="medium",
                detail=f"{path} does not exist.",
                recommendation="Provide /var/log/auth.log or a sample auth log file.",
            )
        ]

    text = log_path.read_text(encoding="utf-8", errors="ignore")
    failed_ips = Counter(match.group("ip") for match in FAILED_RE.finditer(text))
    accepted = [match.groupdict() for match in ACCEPTED_RE.finditer(text)]
    sudo_commands = [match.group("command") for match in SUDO_RE.finditer(text)]
    findings: list[Finding] = []

    if failed_ips:
        top_ip, count = failed_ips.most_common(1)[0]
        severity = "critical" if count >= 10 else "high" if count >= 5 else "medium"
        findings.append(
            Finding(
                title="Failed SSH login attempts detected",
                severity=severity,
                detail=f"{sum(failed_ips.values())} failed SSH attempts found; top source is {top_ip} with {count}.",
                evidence={"top_ips": failed_ips.most_common(5)},
                recommendation="Enable fail2ban, disable password auth, enforce SSH keys, and review firewall rules.",
            )
        )

    if accepted:
        findings.append(
            Finding(
                title="Successful SSH logins found",
                severity="info",
                detail=f"{len(accepted)} successful SSH login events were found.",
                evidence={"sample": accepted[:5]},
                recommendation="Verify users/IPs are expected and correlate with deployment or admin activity.",
            )
        )

    if sudo_commands:
        findings.append(
            Finding(
                title="sudo activity found",
                severity="info",
                detail=f"{len(sudo_commands)} sudo command events were found.",
                evidence={"sample_commands": sudo_commands[:5]},
                recommendation="Review privileged commands for unexpected package, user, firewall, or service changes.",
            )
        )

    return findings or [
        Finding(
            title="No SSH security events detected",
            severity="info",
            detail="No failed SSH, accepted SSH, or sudo events matched the analyzer patterns.",
            recommendation="Confirm the log format and time window.",
        )
    ]
