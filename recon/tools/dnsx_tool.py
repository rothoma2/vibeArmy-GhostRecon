
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import os
from typing import List, Dict
from pprint import pprint
from crewai.tools import tool
import random
import string

@tool("dnsx_bulk_resolve")
def dnsx_bulk_resolve(subdomains: list[str]) -> dict[str, object]:
    """Resolve enumerated subdomains using dnsx and return validated ones with their IPs."""

    print("Inside Tool dnsBulk")
    print(len(subdomains))
    pprint(subdomains)

    if shutil.which("dnsx") is None:
        raise FileNotFoundError(
            "dnsx CLI not found. Install from https://github.com/projectdiscovery/dnsx"
        )

    # Deduplicate and clean input
    items = sorted({s.strip() for s in subdomains if s.strip()})
    if not items:
        return {"resolvable": [], "results": []}
    
    # Generate a small random filename for debugging
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    tmp_file_name = f"/tmp/dnsx_input_{rand_suffix}.txt"

    with open(tmp_file_name, "w", encoding="utf-8") as tmp_file:
        tmp_file.write("\n".join(items))
        tmp_file.flush()

    cmd = [
        "dnsx",
        "-silent",
        "-json",
        "-resp",
        "-l", tmp_file_name,
        "-t", "100",
    ]

    print(f"[DEBUG] Running command: {' '.join(cmd)}")
    print(f"[DEBUG] Input file retained at: {tmp_file_name}")

    results_by_host: Dict[str, set[str]] = {}
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        stderr = proc.stderr.strip().splitlines()
        raise RuntimeError(stderr[-1] if stderr else "dnsx execution failed")
    
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        host = data.get("host") or data.get("name") or data.get("domain")
        if not host:
            continue
        ips = data.get("a", [])
        if isinstance(ips, str):
            ips = [ips]
        elif not isinstance(ips, list):
            ips = []
        cleaned = [ip.strip() for ip in ips if ip.strip()]
        if not cleaned:
            continue
        results_by_host.setdefault(host, set()).update(cleaned)

    resolvable = sorted(results_by_host)
    results = [
        {"host": host, "ips": sorted(list(ips))}
        for host, ips in sorted(results_by_host.items())
    ]
    return {"resolvable": resolvable, "results": results}
