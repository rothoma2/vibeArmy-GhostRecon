from __future__ import annotations

import os
import shutil
import subprocess
from typing import Dict, List

from crewai_tools import tool

from recon.utils import is_valid_domain


@tool("amass_passive_enum")
def amass_passive_enum(domain: str) -> Dict[str, object]:
    """Run "amass enum -passive -d <domain> -silent" and return discovered subdomains.

    The function validates input, ensures authorization, executes Amass in passive
    mode, parses and deduplicates the output, and returns a dictionary with the
    target domain, list of subdomains, and count.
    """
    if not is_valid_domain(domain):
        raise ValueError("Invalid domain provided to Amass tool")
    if os.getenv("AUTHORIZED", "false").lower() != "true":
        raise PermissionError(
            "Authorization required. Set AUTHORIZED=true or use --authorized flag."
        )
    if shutil.which("amass") is None:
        raise FileNotFoundError(
            "Amass CLI not found. Install from https://github.com/owasp-amass/amass"
        )

    try:
        result = subprocess.run(
            ["amass", "enum", "-passive", "-d", domain, "-silent"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Amass execution exceeded 300 seconds") from exc

    if result.returncode != 0:
        stderr_snippet = result.stderr.strip().splitlines()[-1] if result.stderr else ""
        raise RuntimeError(f"Amass failed: {stderr_snippet}")

    subdomains: set[str] = set()
    for line in result.stdout.splitlines():
        hostname = line.strip()
        if not hostname:
            continue
        if is_valid_domain(hostname) and (
            hostname == domain or hostname.endswith(f".{domain}")
        ):
            subdomains.add(hostname)

    sorted_subs: List[str] = sorted(subdomains)
    return {"target_domain": domain, "subdomains": sorted_subs, "count": len(sorted_subs)}
