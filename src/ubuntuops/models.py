from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    title: str
    severity: str
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class IncidentReport:
    issue: str
    summary: str
    findings: list[Finding]
    commands_run: list[str]
