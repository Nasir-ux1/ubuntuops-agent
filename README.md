# UbuntuOps Agent

[![CI](https://github.com/Nasir-ux1/ubuntuops-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Nasir-ux1/ubuntuops-agent/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Nasir-ux1/ubuntuops-agent?include_prereleases&label=release)](https://github.com/Nasir-ux1/ubuntuops-agent/releases/tag/v0.1.0)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

UbuntuOps Agent is an Ubuntu/Linux incident response toolkit that collects diagnostics, detects common failure patterns, recommends fixes, and writes structured incident reports.

It is built as a portfolio-grade Linux/SRE project: practical CLI commands, modular collectors, analyzers, sample logs, tests, and a dashboard.

## Demo

![UbuntuOps CLI screenshot](docs/assets/ubuntuops-cli.png)

![UbuntuOps animated demo](docs/assets/ubuntuops-demo.gif)

## What It Diagnoses

- Failed `systemd` services
- `journalctl` error patterns
- Disk-full incidents
- Deleted-but-open files
- Docker container health and disk usage
- SSH brute-force patterns from `auth.log`
- General system load and memory pressure from `/proc`

## Tech Stack

- Python
- Linux `/proc`
- `systemctl`
- `journalctl`
- `df`, `du`, `lsof`
- Docker CLI
- Streamlit
- unittest

## Project Structure

```text
ubuntuops-agent/
├── app.py
├── src/ubuntuops/
│   ├── collectors/
│   │   ├── system.py
│   │   ├── services.py
│   │   ├── disk.py
│   │   └── docker.py
│   ├── analyzers/
│   │   ├── service_doctor.py
│   │   ├── disk_doctor.py
│   │   ├── ssh_analyzer.py
│   │   └── docker_doctor.py
│   ├── agent.py
│   ├── cli.py
│   ├── report.py
│   └── models.py
├── samples/
├── tests/
└── reports/
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## CLI Examples

Run natural-language diagnosis:

```bash
PYTHONPATH=src python -m ubuntuops.cli diagnose --issue "ssh login attempts are high" --auth-log samples/auth.log
```

Diagnose a service:

```bash
PYTHONPATH=src python -m ubuntuops.cli service nginx
```

Analyze a saved service failure log:

```bash
PYTHONPATH=src python -m ubuntuops.cli service nginx --journal-file samples/journal_nginx_failed.log
```

Run disk RCA:

```bash
PYTHONPATH=src python -m ubuntuops.cli disk --path /
```

Analyze SSH logs:

```bash
PYTHONPATH=src python -m ubuntuops.cli ssh --log samples/auth.log
```

Run Docker checks:

```bash
PYTHONPATH=src python -m ubuntuops.cli docker
```

Run the dashboard:

```bash
streamlit run app.py
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Example Finding

```text
[HIGH] Failed SSH login attempts detected:
4 failed SSH attempts found; top source is 203.0.113.10 with 3.
Fix: Enable fail2ban, disable password auth, enforce SSH keys, and review firewall rules.
```
