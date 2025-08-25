from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path


def is_valid_domain(domain: str) -> bool:
    """Return True if the domain is a valid FQDN."""
    if not domain:
        return False
    fqdn_regex = re.compile(
        r"^(?=.{4,253}$)([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[A-Za-z]{2,}$"
    )
    return bool(fqdn_regex.fullmatch(domain))


def ensure_outputs_dir() -> Path:
    """Ensure the outputs directory exists and return its Path."""
    path = Path("outputs")
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_list(path: Path, items: list[str]) -> None:
    """Write a JSON list to the given path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def prompt_for_domain() -> str:
    """Prompt the user for a domain until a valid one is provided."""
    while True:
        try:
            domain = input("Enter target domain: ").strip()
        except EOFError:  # User cancelled
            sys.exit(1)
        if not domain:
            sys.exit(1)
        if is_valid_domain(domain):
            return domain
        logging.error("Invalid domain. Please enter a valid FQDN.")
