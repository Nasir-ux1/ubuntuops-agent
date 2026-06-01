from __future__ import annotations

from pathlib import Path

from ubuntuops.runner import command_exists, run_command


def collect_disk_report(path: str = "/") -> dict[str, object]:
    usage = run_command(["df", "-h", path], timeout=8) if command_exists("df") else None
    largest = (
        run_command(["du", "-xhd1", path], timeout=15)
        if command_exists("du") and Path(path).exists()
        else None
    )
    deleted_open = run_command(["lsof", "+L1"], timeout=10) if command_exists("lsof") else None
    docker_usage = run_command(["docker", "system", "df"], timeout=10) if command_exists("docker") else None

    return {
        "path": path,
        "usage": usage.stdout if usage else "",
        "largest": largest.stdout if largest else "",
        "deleted_open_files": deleted_open.stdout if deleted_open else "",
        "docker_usage": docker_usage.stdout if docker_usage else "",
    }
