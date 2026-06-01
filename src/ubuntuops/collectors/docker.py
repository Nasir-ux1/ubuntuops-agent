from __future__ import annotations

from ubuntuops.runner import command_exists, run_command


def collect_docker_health() -> dict[str, object]:
    if not command_exists("docker"):
        return {"available": False, "containers": "", "disk_usage": ""}
    containers = run_command(["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"])
    disk_usage = run_command(["docker", "system", "df"])
    return {
        "available": True,
        "containers": containers.stdout or containers.stderr,
        "disk_usage": disk_usage.stdout or disk_usage.stderr,
    }
