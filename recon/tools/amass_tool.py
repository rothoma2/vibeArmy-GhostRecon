from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, List

from crewai.tools import tool

from recon.utils import is_valid_domain


@tool("amass_passive_enum")
def amass_passive_enum(domain: str) -> Dict[str, object]:
    """Run "amass enum -passive -d <domain> -silent" and return discovered subdomains.

    The function validates input, executes Amass in passive
    mode, parses and deduplicates the output, and returns a dictionary with the
    target domain, list of subdomains, and count.
    """
    print("Running Amass tool.")

    if not is_valid_domain(domain):
        raise ValueError("Invalid domain provided to Amass tool")

    if shutil.which("amass") is None:
        raise FileNotFoundError(
            "Amass CLI not found. Install from https://github.com/owasp-amass/amass"
        )

    # Run the passive enumeration command first
    enum_cmd = ["amass", "enum", "-passive", "-d", domain]
    print(f"Debug: Running command: {' '.join(enum_cmd)}")
    try:
        enum_result = subprocess.run(
            enum_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Amass enum execution exceeded 120 seconds") from exc

    if enum_result.returncode != 0:
        stderr_snippet = enum_result.stderr.strip().splitlines()[-1] if enum_result.stderr else ""
        raise RuntimeError(f"Amass enum failed: {stderr_snippet}")

    # Now run the db command to extract discovered FQDNs
    db_cmd = ["amass", "db", "-names", "-d", domain]
    print(f"Debug: Running command: {' '.join(db_cmd)}")
    try:
        db_result = subprocess.run(
            db_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Amass db execution exceeded 60 seconds") from exc

    if db_result.returncode != 0:
        stderr_snippet = db_result.stderr.strip().splitlines()[-1] if db_result.stderr else ""
        raise RuntimeError(f"Amass db failed: {stderr_snippet}")

    subdomains: set[str] = set()
    for line in db_result.stdout.splitlines():
        hostname = line.strip()
        if not hostname:
            continue
        if is_valid_domain(hostname) and (
            hostname == domain or hostname.endswith(f".{domain}")
        ):
            subdomains.add(hostname)

    sorted_subs: List[str] = sorted(subdomains)
    return {"target_domain": domain, "subdomains": sorted_subs, "count": len(sorted_subs)}
