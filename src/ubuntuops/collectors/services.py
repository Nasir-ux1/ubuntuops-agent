from __future__ import annotations

from ubuntuops.runner import command_exists, run_command


def collect_service_status(service: str) -> dict[str, object]:
    if not command_exists("systemctl"):
        return {"service": service, "available": False, "status": "", "journal": ""}

    status = run_command(["systemctl", "status", service, "--no-pager"], timeout=8)
    journal = run_command(["journalctl", "-u", service, "-n", "80", "--no-pager"], timeout=8)
    return {
        "service": service,
        "available": True,
        "status": status.stdout or status.stderr,
        "journal": journal.stdout or journal.stderr,
        "status_code": status.returncode,
        "journal_code": journal.returncode,
    }


def collect_failed_services() -> dict[str, object]:
    if not command_exists("systemctl"):
        return {"available": False, "failed": ""}
    result = run_command(["systemctl", "--failed", "--no-pager"], timeout=8)
    return {"available": True, "failed": result.stdout or result.stderr}
