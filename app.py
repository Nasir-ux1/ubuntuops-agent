from __future__ import annotations

from pathlib import Path

import streamlit as st

from ubuntuops.agent import diagnose_issue
from ubuntuops.report import write_incident_report


st.set_page_config(page_title="UbuntuOps Agent", layout="wide")
st.title("UbuntuOps Agent")
st.caption("AI-assisted Ubuntu incident response, diagnostics, and report generation")

issue = st.text_input("Issue", "nginx is down")
service = st.text_input("Service name", "nginx")
auth_log = st.text_input("Auth log path", "samples/auth.log")

if st.button("Run diagnosis", type="primary"):
    report = diagnose_issue(issue, service or None, auth_log or None)
    path = write_incident_report(report)

    st.subheader("Summary")
    st.write(report.summary)

    st.subheader("Findings")
    for finding in report.findings:
        st.markdown(f"**{finding.title}**")
        st.write(f"Severity: `{finding.severity}`")
        st.write(finding.detail)
        st.info(finding.recommendation or "Review the evidence and investigate further.")
        st.json(finding.evidence)

    st.subheader("Report")
    st.download_button(
        "Download incident report",
        Path(path).read_text(encoding="utf-8"),
        file_name="incident_report.md",
    )
