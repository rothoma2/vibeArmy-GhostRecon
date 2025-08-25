from __future__ import annotations

import logging
import os
from typing import Dict, Optional

from crewai import Crew, Process

from recon.agents import passive_recon_agent
from recon.tasks import (
    summarize_subdomains_task,
    passive_enum_task,
    validate_subdomains_task,
)
from recon.utils import prompt_for_domain


def run(target_domain: Optional[str]) -> Dict[str, object]:
    """Run the recon crew and return the passive enumeration result."""
    domain = target_domain or prompt_for_domain()
    logging.info("Using target domain: %s", domain)

    crew = Crew(
        agents=[passive_recon_agent],
        tasks=[
            passive_enum_task,
            validate_subdomains_task,
            summarize_subdomains_task,
        ],
        process=Process.sequential,
    )

    result = crew.kickoff(inputs={"target_domain": domain})
    return result

__all__ = ["run"]
