from __future__ import annotations

import shutil
import subprocess

from ubuntuops.models import CommandResult


def command_exists(binary: str) -> bool:
    return shutil.which(binary) is not None


def run_command(command: list[str], timeout: int = 8) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return CommandResult(command=command, returncode=127, stdout="", stderr=str(exc))
