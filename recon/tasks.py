from __future__ import annotations

from crewai import Task

from recon.agents import passive_recon_agent


domain_intake_task = Task(
    description=(
        "If {target_domain} is missing, obtain it from the user interactively via CLI "
        "before proceeding. Validate it strictly as an FQDN."
    ),
    expected_output="A validated target_domain string assigned to target_domain input.",
    agent=passive_recon_agent,
)

passive_enum_task = Task(
    description=(
        "For {target_domain}, perform passive subdomain enumeration using the provided "
        "Amass tool. Do not use any active techniques. Provide a list of enumerated_subdomains."
    ),
    expected_output=(
        "A dictionary with keys: target_domain (str), count (int), and enumerated_subdomains (list[str])."
    ),
    agent=passive_recon_agent,
)

validate_subdomains_task = Task(
    description=(
        "Validate the list of previous enumerated_subdomains using"
        "dnsx_bulk_resolve tool. Return JSON with keys 'validated_subdomains' and 'results' "
        "listing resolved hosts and their IP addresses."
    ),
    expected_output=(
        "A JSON object with keys: validated_subdomains (list[str]) and results (list[dict{host: str, ips: list[str]}])."
    ),
    agent=passive_recon_agent,
)

summarize_subdomains_task = Task(
    description=(
        "For {target_domain}, use the count_unique_subdomains tool to count how many unique validated_subdomains were found. "
        "Return only the count and a brief summary."
    ),
    expected_output="An integer count of unique validated_subdomains and a one-sentence summary.",
    agent=passive_recon_agent,
)

__all__ = ["domain_intake_task", "passive_enum_task"]
__all__.append("summarize_subdomains_task")
__all__.append("validate_subdomains_task")
