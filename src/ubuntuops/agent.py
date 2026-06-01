from __future__ import annotations

import re

from ubuntuops.analyzers.disk_doctor import analyze_disk
from ubuntuops.analyzers.docker_doctor import analyze_docker
from ubuntuops.analyzers.service_doctor import analyze_service
from ubuntuops.analyzers.ssh_analyzer import analyze_auth_log
from ubuntuops.collectors.disk import collect_disk_report
from ubuntuops.collectors.docker import collect_docker_health
from ubuntuops.collectors.services import collect_failed_services, collect_service_status
from ubuntuops.collectors.system import collect_system_health
from ubuntuops.models import Finding, IncidentReport
from ubuntuops.report import summarize_findings


def diagnose_issue(issue: str, service: str | None = None, auth_log: str | None = None) -> IncidentReport:
    normalized = issue.lower()
    findings: list[Finding] = []
    commands_run: list[str] = []

    if _mentions_disk(normalized):
        findings.extend(analyze_disk(collect_disk_report("/")))
        commands_run.extend(["df -h /", "du -xhd1 /", "lsof +L1", "docker system df"])

    if _mentions_ssh(normalized) or auth_log:
        log_path = auth_log or "/var/log/auth.log"
        findings.extend(analyze_auth_log(log_path))
        commands_run.append(f"read {log_path}")

    if _mentions_docker(normalized):
        findings.extend(analyze_docker(collect_docker_health()))
        commands_run.extend(["docker ps -a", "docker system df"])

    inferred_service = service or _extract_service_name(normalized)
    if inferred_service:
        findings.extend(analyze_service(collect_service_status(inferred_service)))
        commands_run.extend(
            [
                f"systemctl status {inferred_service} --no-pager",
                f"journalctl -u {inferred_service} -n 80 --no-pager",
            ]
        )

    if not findings:
        findings.extend(_analyze_general_health())
        commands_run.extend(["cat /proc/loadavg", "cat /proc/meminfo", "cat /proc/net/dev"])
        failed = collect_failed_services()
        if failed.get("available"):
            findings.append(
                Finding(
                    title="Failed service inventory collected",
                    severity="info",
                    detail="systemctl --failed output was collected for broad triage.",
                    evidence={"failed_services": str(failed.get("failed", ""))[:1200]},
                    recommendation="Investigate any failed units first, then check resource pressure.",
                )
            )
            commands_run.append("systemctl --failed --no-pager")

    return IncidentReport(
        issue=issue,
        summary=summarize_findings(issue, findings),
        findings=findings,
        commands_run=commands_run,
    )


def _analyze_general_health() -> list[Finding]:
    health = collect_system_health()
    findings: list[Finding] = []
    load = health.get("loadavg", {})
    memory = health.get("memory", {})
    cpu_count = health.get("cpu_count") or 1

    if isinstance(load, dict) and load.get("1m") is not None:
        load_1m = float(load["1m"])
        severity = "high" if load_1m > float(cpu_count) * 2 else "info"
        findings.append(
            Finding(
                title="System load collected",
                severity=severity,
                detail=f"1-minute load average is {load_1m} across {cpu_count} CPUs.",
                evidence={"loadavg": load, "cpu_count": cpu_count},
                recommendation="If load is high, inspect top CPU processes, disk wait, and stuck services.",
            )
        )

    if isinstance(memory, dict) and memory.get("MemTotal") and memory.get("MemAvailable"):
        total = int(memory["MemTotal"])
        available = int(memory["MemAvailable"])
        used_pct = round((1 - available / total) * 100, 2)
        severity = "high" if used_pct >= 90 else "medium" if used_pct >= 80 else "info"
        findings.append(
            Finding(
                title="Memory pressure collected",
                severity=severity,
                detail=f"Estimated memory usage is {used_pct}%.",
                evidence={"used_pct": used_pct, "mem_total_kb": total, "mem_available_kb": available},
                recommendation="If memory is high, inspect top memory processes and OOM events in journalctl.",
            )
        )

    return findings or [
        Finding(
            title="General health unavailable",
            severity="medium",
            detail="UbuntuOps could not collect live /proc health data in this environment.",
            recommendation="Run on an Ubuntu host or WSL instance for full live diagnostics.",
        )
    ]


def _mentions_disk(issue: str) -> bool:
    return any(token in issue for token in ("disk", "space", "storage", "filesystem", "volume"))


def _mentions_ssh(issue: str) -> bool:
    return any(token in issue for token in ("ssh", "login", "brute", "auth"))


def _mentions_docker(issue: str) -> bool:
    return any(token in issue for token in ("docker", "container", "image"))


def _extract_service_name(issue: str) -> str | None:
    common = ["nginx", "apache2", "mysql", "postgresql", "docker", "ssh", "redis"]
    for service in common:
        if re.search(rf"\b{re.escape(service)}\b", issue):
            return service
    match = re.search(r"\bservice\s+([\w@.-]+)", issue)
    return match.group(1) if match else None
