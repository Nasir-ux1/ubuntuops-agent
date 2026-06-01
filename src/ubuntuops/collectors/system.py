from __future__ import annotations

import os
from pathlib import Path


def collect_system_health() -> dict[str, object]:
    return {
        "loadavg": _read_loadavg(),
        "memory": _read_meminfo(),
        "disk_mounts": _read_mounts(),
        "network_interfaces": _read_netdev(),
        "cpu_count": os.cpu_count(),
    }


def _read_loadavg() -> dict[str, float | None]:
    path = Path("/proc/loadavg")
    if not path.exists():
        return {"1m": None, "5m": None, "15m": None}
    parts = path.read_text(encoding="utf-8").split()
    return {"1m": float(parts[0]), "5m": float(parts[1]), "15m": float(parts[2])}


def _read_meminfo() -> dict[str, int]:
    path = Path("/proc/meminfo")
    if not path.exists():
        return {}
    values: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        key, raw = line.split(":", 1)
        number = raw.strip().split()[0]
        if number.isdigit():
            values[key] = int(number)
    return values


def _read_mounts() -> list[dict[str, str]]:
    path = Path("/proc/mounts")
    if not path.exists():
        return []
    mounts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 3:
            mounts.append({"device": parts[0], "mount": parts[1], "fstype": parts[2]})
    return mounts


def _read_netdev() -> dict[str, dict[str, int]]:
    path = Path("/proc/net/dev")
    if not path.exists():
        return {}
    interfaces: dict[str, dict[str, int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[2:]:
        name, data = line.split(":", 1)
        fields = data.split()
        interfaces[name.strip()] = {
            "rx_bytes": int(fields[0]),
            "rx_errors": int(fields[2]),
            "tx_bytes": int(fields[8]),
            "tx_errors": int(fields[10]),
        }
    return interfaces
