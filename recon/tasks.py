from __future__ import annotations

from crewai import Task

from recon.agents import passive_recon_agent


domain_intake_task = Task(
    description=(
        "If {target_domain} is missing, obtain it from the user interactively via CLI "
        "before proceeding. Validate it strictly as an FQDN."
    ),
    expected_output="A validated domain string assigned to target_domain input.",
    agent=passive_recon_agent,
)

passive_enum_task = Task(
    description=(
        "For {target_domain}, perform passive subdomain enumeration using the provided "
        "Amass tool. Do not use any active techniques. Provide a concise textual "
        "summary and the final list of subdomains."
    ),
    expected_output=(
        "A dictionary with keys: target_domain (str), count (int), and subdomains (list[str])."
    ),
    agent=passive_recon_agent,
)

__all__ = ["domain_intake_task", "passive_enum_task"]
