from __future__ import annotations

import argparse
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from recon.crew import run as run_crew
from recon.utils import (
    ensure_outputs_dir,
    is_valid_domain,
    prompt_for_domain,
    write_json_list,
)


logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logging.getLogger("crewAI").setLevel(logging.INFO)
logging.getLogger("langchain").setLevel(logging.INFO)

def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Passive recon using Amass (passive mode only).")
    parser.add_argument("--domain", "-d", help="Target domain")
    parser.add_argument("--authorized", action="store_true", help="Confirm you are authorized to run this tool")
    args = parser.parse_args()

    domain: Optional[str] = args.domain
    if domain and not is_valid_domain(domain):
        logging.error("Invalid domain provided via --domain option.")
        raise SystemExit(1)
    if not domain:
        domain = prompt_for_domain()

    try:
        result = run_crew(domain)
    except Exception as exc:  # pylint: disable=broad-except
        logging.error("%s", exc)
        raise SystemExit(1) from exc

    # subdomains = result.get("subdomains", []) if isinstance(result, dict) else []
    # outputs_dir = ensure_outputs_dir()
    # out_path = outputs_dir / f"{result.get('target_domain', 'domain')}_subdomains.json"
    # write_json_list(out_path, subdomains)

    # print(
    #     f"{result.get('target_domain')}: {len(subdomains)} subdomains written to {out_path}"
    # )


if __name__ == "__main__":
    main()
