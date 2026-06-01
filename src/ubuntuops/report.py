from __future__ import annotations

from pathlib import Path

from ubuntuops.models import Finding, IncidentReport


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "info": 3}


def summarize_findings(issue: str, findings: list[Finding]) -> str:
    if not findings:
        return f"No findings were produced for: {issue}."
    sorted_findings = sorted(findings, key=lambda item: SEVERITY_ORDER.get(item.severity, 9))
    top = sorted_findings[0]
    return f"Top finding: {top.title} ({top.severity}). {top.detail}"


def write_incident_report(report: IncidentReport, output_dir: str = "reports") -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    report_path = path / "incident_report.md"

    lines = [
        "# UbuntuOps Incident Report",
        "",
        f"**Issue:** {report.issue}",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        "## Findings",
        "",
    ]

    for index, finding in enumerate(
        sorted(report.findings, key=lambda item: SEVERITY_ORDER.get(item.severity, 9)),
        start=1,
    ):
        lines.extend(
            [
                f"### {index}. {finding.title}",
                "",
                f"- Severity: `{finding.severity}`",
                f"- Detail: {finding.detail}",
                f"- Recommendation: {finding.recommendation or 'Review evidence and investigate further.'}",
                f"- Evidence: `{finding.evidence}`",
                "",
            ]
        )

    if report.commands_run:
        lines.extend(["## Commands Used", ""])
        for command in report.commands_run:
            lines.append(f"- `{command}`")
        lines.append("")

    lines.extend(
        [
            "## Prevention Checklist",
            "",
            "- Add monitoring for the affected component.",
            "- Add a runbook entry for the detected failure mode.",
            "- Review recent deploys, package changes, and configuration changes.",
            "- Add alert thresholds before the issue becomes user-impacting.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
