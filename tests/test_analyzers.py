from __future__ import annotations

import unittest
from pathlib import Path

from ubuntuops.analyzers.disk_doctor import analyze_disk
from ubuntuops.analyzers.service_doctor import analyze_service
from ubuntuops.analyzers.ssh_analyzer import analyze_auth_log
from ubuntuops.agent import diagnose_issue


ROOT = Path(__file__).resolve().parents[1]


class UbuntuOpsAnalyzerTests(unittest.TestCase):
    def test_service_doctor_detects_port_conflict(self) -> None:
        journal = (ROOT / "samples" / "journal_nginx_failed.log").read_text(encoding="utf-8")
        findings = analyze_service(
            {
                "service": "nginx",
                "available": True,
                "status": "Active: failed",
                "journal": journal,
            }
        )

        self.assertTrue(any(finding.title == "Port already in use" for finding in findings))

    def test_disk_doctor_detects_critical_usage(self) -> None:
        findings = analyze_disk(
            {
                "usage": "Filesystem Size Used Avail Use% Mounted on\n/dev/sda1 20G 19G 1G 95% /",
                "largest": "10G /var",
                "deleted_open_files": "",
                "docker_usage": "",
            }
        )

        self.assertTrue(any(finding.severity == "critical" for finding in findings))

    def test_ssh_analyzer_detects_failed_attempts(self) -> None:
        findings = analyze_auth_log(str(ROOT / "samples" / "auth.log"))

        self.assertTrue(any("SSH" in finding.title for finding in findings))

    def test_agent_uses_auth_log_for_ssh_issue(self) -> None:
        report = diagnose_issue(
            "ssh login attempts are high",
            auth_log=str(ROOT / "samples" / "auth.log"),
        )

        self.assertTrue(report.findings)
        self.assertIn("SSH", report.summary)


if __name__ == "__main__":
    unittest.main()
