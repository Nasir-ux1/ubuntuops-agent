from __future__ import annotations

import re

from ubuntuops.models import Finding


def analyze_docker(docker_data: dict[str, object]) -> list[Finding]:
    if not docker_data.get("available"):
        return [
            Finding(
                title="Docker unavailable",
                severity="info",
                detail="Docker CLI is not available in this environment.",
                recommendation="Run Docker diagnostics on a host with Docker installed.",
            )
        ]

    containers = str(docker_data.get("containers", ""))
    disk_usage = str(docker_data.get("disk_usage", ""))
    findings: list[Finding] = []

    unhealthy = []
    for line in containers.splitlines():
        if re.search(r"restarting|exited|unhealthy", line, re.I):
            unhealthy.append(line)

    if unhealthy:
        findings.append(
            Finding(
                title="Unhealthy Docker containers",
                severity="high",
                detail=f"{len(unhealthy)} containers are not healthy/running cleanly.",
                evidence={"containers": unhealthy[:10]},
                recommendation="Inspect docker logs, restart policy, healthcheck, image version, ports, and env vars.",
            )
        )

    if disk_usage.strip():
        findings.append(
            Finding(
                title="Docker disk usage collected",
                severity="info",
                detail="Docker disk usage summary is available.",
                evidence={"docker_system_df": disk_usage[:1000]},
                recommendation="Review unused images, stopped containers, build cache, and volumes before pruning.",
            )
        )

    return findings or [
        Finding(
            title="No Docker issue detected",
            severity="info",
            detail="No unhealthy Docker container pattern matched.",
            recommendation="Use docker logs for application-level failures.",
        )
    ]
