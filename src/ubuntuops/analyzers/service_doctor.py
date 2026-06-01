from __future__ import annotations

import re

from ubuntuops.models import Finding


PATTERNS = [
    (
        "Permission denied",
        "high",
        re.compile(r"permission denied|access denied", re.I),
        "Check file ownership, executable bits, AppArmor/SELinux policy, and service user permissions.",
    ),
    (
        "Port already in use",
        "high",
        re.compile(r"address already in use|bind.*failed|port.*in use", re.I),
        "Find the process using the port with ss/lsof, stop the conflicting service, or change the service port.",
    ),
    (
        "Missing file or directory",
        "high",
        re.compile(r"no such file|not found|cannot access", re.I),
        "Verify ExecStart paths, config file paths, mounted volumes, and package installation.",
    ),
    (
        "Restart loop",
        "medium",
        re.compile(r"start request repeated too quickly|restart counter|failed with result", re.I),
        "Inspect the first failure in journalctl, fix the underlying error, then reset-failed and restart.",
    ),
    (
        "Configuration error",
        "medium",
        re.compile(r"syntax error|invalid config|configuration file.*test failed", re.I),
        "Run the service-specific config test command, fix syntax, and reload the unit.",
    ),
]


def analyze_service(service_data: dict[str, object]) -> list[Finding]:
    service = str(service_data.get("service", "unknown"))
    text = f"{service_data.get('status', '')}\n{service_data.get('journal', '')}"
    findings: list[Finding] = []

    if not service_data.get("available"):
        return [
            Finding(
                title="systemd unavailable",
                severity="medium",
                detail="systemctl is not available in this environment, so live service diagnosis was skipped.",
                recommendation="Run this module on an Ubuntu host with systemd.",
            )
        ]

    for title, severity, pattern, recommendation in PATTERNS:
        if pattern.search(text):
            findings.append(
                Finding(
                    title=title,
                    severity=severity,
                    detail=f"{service} logs match a known failure pattern: {title}.",
                    evidence={"service": service, "matched_pattern": pattern.pattern},
                    recommendation=recommendation,
                )
            )

    active_failed = re.search(r"Active:\s+failed|Loaded:.*not-found", text, re.I)
    if active_failed and not findings:
        findings.append(
            Finding(
                title="Service is failed",
                severity="high",
                detail=f"{service} appears failed, but no specific known pattern matched.",
                evidence={"service": service},
                recommendation="Review the earliest journal error after the last start attempt and validate config/dependencies.",
            )
        )

    if not findings:
        findings.append(
            Finding(
                title="No obvious service failure pattern",
                severity="info",
                detail=f"No high-confidence failure pattern was found for {service}.",
                evidence={"service": service},
                recommendation="Check recent deploys, environment files, dependencies, and resource pressure.",
            )
        )

    return findings
