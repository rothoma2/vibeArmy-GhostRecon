from __future__ import annotations

import logging
import os
from typing import Dict, Optional

from crewai import Crew, Process

from recon.agents import passive_recon_agent
from recon.tasks import domain_intake_task, passive_enum_task
from recon.utils import prompt_for_domain


def run(target_domain: Optional[str], authorized: bool) -> Dict[str, object]:
    """Run the recon crew and return the passive enumeration result."""
    domain = target_domain or prompt_for_domain()
    logging.info("Using target domain: %s", domain)

    if authorized:
        os.environ["AUTHORIZED"] = "true"

    crew = Crew(
        agents=[passive_recon_agent],
        tasks=[domain_intake_task, passive_enum_task],
        process=Process.sequential,
    )

    result = crew.run(inputs={"target_domain": domain})
    return result

__all__ = ["run"]
