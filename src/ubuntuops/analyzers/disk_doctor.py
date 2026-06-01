from __future__ import annotations

import re

from ubuntuops.models import Finding


def analyze_disk(disk_data: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    usage = str(disk_data.get("usage", ""))
    largest = str(disk_data.get("largest", ""))
    deleted_open = str(disk_data.get("deleted_open_files", ""))
    docker_usage = str(disk_data.get("docker_usage", ""))

    percent = _extract_highest_usage_percent(usage)
    if percent is not None and percent >= 90:
        findings.append(
            Finding(
                title="Disk usage is critical",
                severity="critical",
                detail=f"Filesystem usage is at {percent}%.",
                evidence={"usage_percent": percent, "df": usage},
                recommendation="Identify the largest directories, rotate logs, prune unused Docker data, and expand storage if needed.",
            )
        )
    elif percent is not None and percent >= 80:
        findings.append(
            Finding(
                title="Disk usage is high",
                severity="medium",
                detail=f"Filesystem usage is at {percent}%.",
                evidence={"usage_percent": percent},
                recommendation="Review growth trend and clean old logs/package caches before it becomes critical.",
            )
        )

    if deleted_open.strip():
        findings.append(
            Finding(
                title="Deleted files still held open",
                severity="high",
                detail="lsof found deleted files still held by running processes.",
                evidence={"deleted_open_files": deleted_open[:1000]},
                recommendation="Restart the owning process after confirming it is safe.",
            )
        )

    if "GB" in docker_usage or "MB" in docker_usage:
        findings.append(
            Finding(
                title="Docker disk usage available",
                severity="info",
                detail="Docker system disk usage was collected for cleanup review.",
                evidence={"docker_system_df": docker_usage[:1000]},
                recommendation="Use docker system prune only after confirming unused images/volumes are not needed.",
            )
        )

    if largest.strip():
        top_line = largest.splitlines()[-1] if largest.splitlines() else ""
        findings.append(
            Finding(
                title="Largest directory sample collected",
                severity="info",
                detail="Top-level disk usage data is available for RCA.",
                evidence={"du_sample": top_line},
                recommendation="Sort du output and inspect the largest application/log directories first.",
            )
        )

    return findings or [
        Finding(
            title="No disk issue detected",
            severity="info",
            detail="Disk diagnostics did not show a clear issue from available data.",
            recommendation="Run on the target Ubuntu host for live disk data.",
        )
    ]


def _extract_highest_usage_percent(df_output: str) -> int | None:
    matches = [int(value) for value in re.findall(r"\b(\d{1,3})%", df_output)]
    return max(matches) if matches else None
