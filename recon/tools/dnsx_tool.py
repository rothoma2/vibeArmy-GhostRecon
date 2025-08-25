from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Dict, List, Sequence

from crewai.tools import tool


@tool("dnsx_bulk_resolve")
def dnsx_bulk_resolve(
    subdomains: str | Sequence[str],
    threads: int = 100,
    resolvers: Sequence[str] | None = None,
    timeout: int = 5000,
    retries: int = 2,
    include_ipv6: bool = False,
) -> Dict[str, object]:
    """Resolve many subdomains quickly using ProjectDiscovery's dnsx.

    Parameters
    ----------
    subdomains: str | Sequence[str]
        Candidate subdomains as newline-separated string or iterable of strings.
    threads: int, optional
        Number of concurrent threads for dnsx. Defaults to 100.
    resolvers: Sequence[str] | None, optional
        Custom DNS resolvers to use. If provided, joined by comma and passed to
        dnsx via ``-r`` option.
    timeout: int, optional
        Timeout in milliseconds for each DNS query. Defaults to 5000.
    retries: int, optional
        Number of retry attempts dnsx should make. Defaults to 2.
    include_ipv6: bool, optional
        When True, also query AAAA (IPv6) records.

    Returns
    -------
    Dict[str, object]
        Dictionary with keys ``resolvable`` (sorted list of hosts that resolved)
        and ``results`` (list of objects with ``host`` and ``ips``).
    """
    if shutil.which("dnsx") is None:
        raise FileNotFoundError(
            "dnsx CLI not found. Install from https://github.com/projectdiscovery/dnsx"
        )

    # Normalize input into ordered, deduplicated list
    if isinstance(subdomains, str):
        raw_items = [line.strip() for line in subdomains.splitlines()]
    else:
        raw_items = [str(item).strip() for item in subdomains]
    seen: set[str] = set()
    items: List[str] = []
    for item in raw_items:
        if not item or item in seen:
            continue
        seen.add(item)
        items.append(item)

    if not items:
        return {"resolvable": [], "results": []}

    tmp_file = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
    try:
        tmp_file.write("\n".join(items))
        tmp_file.flush()
        tmp_file.close()

        base_cmd = [
            "dnsx",
            "-silent",
            "-json",
            "-resp",
            "-l",
            tmp_file.name,
            "-t",
            str(threads),
            "-retry",
            str(retries),
            "-timeout",
            str(timeout),
        ]
        if resolvers:
            base_cmd.extend(["-r", ",".join(resolvers)])

        query_flags = ["-a"]
        if include_ipv6:
            query_flags.append("-aaaa")

        results_by_host: Dict[str, set[str]] = {}
        for q in query_flags:
            cmd = base_cmd + [q]
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
                ips: List[str] = []
                for key in ("a", "aaaa", "resp"):
                    value = data.get(key)
                    if isinstance(value, list):
                        ips.extend(str(v) for v in value)
                    elif isinstance(value, str):
                        ips.append(value)
                cleaned = [ip for ip in {ip.strip() for ip in ips} if ip]
                if not cleaned:
                    continue
                results_by_host.setdefault(host, set()).update(cleaned)

        resolvable = sorted(results_by_host)
        results = [
            {"host": host, "ips": sorted(list(ips))}
            for host, ips in sorted(results_by_host.items())
        ]
        return {"resolvable": resolvable, "results": results}
    finally:
        try:
            os.unlink(tmp_file.name)
        except OSError:
            pass
