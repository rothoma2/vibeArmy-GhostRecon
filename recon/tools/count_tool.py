from __future__ import annotations

from crewai.tools import tool
from typing import Any

@tool("count_unique_subdomains")
def count_unique_subdomains(subdomains: list[str]) -> dict[str, Any]:
    """Count unique subdomains in a list and return the count and a summary."""
    unique = {s.strip().lower() for s in subdomains if s}
    count = len(unique)
    return {
        "count": count,
        "unique": sorted(unique),
        "summary": f"Found {count} unique subdomains."
    }