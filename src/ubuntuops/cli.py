from __future__ import annotations

import argparse

from ubuntuops.agent import diagnose_issue
from ubuntuops.analyzers.disk_doctor import analyze_disk
from ubuntuops.analyzers.docker_doctor import analyze_docker
from ubuntuops.analyzers.service_doctor import analyze_service
from ubuntuops.analyzers.ssh_analyzer import analyze_auth_log
from ubuntuops.collectors.disk import collect_disk_report
from ubuntuops.collectors.docker import collect_docker_health
from ubuntuops.collectors.services import collect_service_status
from ubuntuops.report import write_incident_report


def main() -> None:
    parser = argparse.ArgumentParser(description="UbuntuOps Agent: Ubuntu incident diagnostics.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose = subparsers.add_parser("diagnose", help="Diagnose a natural-language issue.")
    diagnose.add_argument("--issue", required=True, help="Issue description, e.g. 'nginx is down'.")
    diagnose.add_argument("--service", help="Optional explicit systemd service name.")
    diagnose.add_argument("--auth-log", help="Optional auth.log path for SSH analysis.")
    diagnose.add_argument("--output-dir", default="reports", help="Report output directory.")

    service = subparsers.add_parser("service", help="Diagnose one systemd service.")
    service.add_argument("name")
    service.add_argument("--journal-file", help="Analyze a saved journalctl log instead of live systemd.")

    disk = subparsers.add_parser("disk", help="Run disk RCA.")
    disk.add_argument("--path", default="/")

    ssh = subparsers.add_parser("ssh", help="Analyze SSH/auth logs.")
    ssh.add_argument("--log", default="/var/log/auth.log")

    subparsers.add_parser("docker", help="Run Docker health checks.")

    args = parser.parse_args()

    if args.command == "diagnose":
        report = diagnose_issue(args.issue, args.service, args.auth_log)
        path = write_incident_report(report, args.output_dir)
        print(report.summary)
        print(f"Report written to: {path}")
        _print_findings(report.findings)
    elif args.command == "service":
        if args.journal_file:
            from pathlib import Path

            journal = Path(args.journal_file).read_text(encoding="utf-8", errors="ignore")
            data = {"service": args.name, "available": True, "status": "sample log", "journal": journal}
        else:
            data = collect_service_status(args.name)
        _print_findings(analyze_service(data))
    elif args.command == "disk":
        _print_findings(analyze_disk(collect_disk_report(args.path)))
    elif args.command == "ssh":
        _print_findings(analyze_auth_log(args.log))
    elif args.command == "docker":
        _print_findings(analyze_docker(collect_docker_health()))


def _print_findings(findings) -> None:
    for finding in findings:
        print(f"[{finding.severity.upper()}] {finding.title}: {finding.detail}")
        if finding.recommendation:
            print(f"  Fix: {finding.recommendation}")


if __name__ == "__main__":
    main()
