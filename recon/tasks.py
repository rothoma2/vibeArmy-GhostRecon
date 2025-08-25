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

validate_subdomains_task = Task(
    description=(
        "Validate candidate subdomains from {candidate_subdomains} using the "
        "dnsx_bulk_resolve tool. Return JSON with keys 'resolvable' and 'results' "
        "listing resolved hosts and their IP addresses."
    ),
    expected_output=(
        "A JSON object with keys: resolvable (list[str]) and results (list[dict{host: str, ips: list[str]}])."
    ),
    agent=passive_recon_agent,
)

# Summarize task: count unique subdomains enumerated for the target domain
summarize_subdomains_task = Task(
    description=(
        "For {target_domain}, use the count_unique_subdomains tool to count how many unique subdomains were enumerated. "
        "Return only the count and a brief summary."
    ),
    expected_output="An integer count of unique subdomains and a one-sentence summary.",
    agent=passive_recon_agent,
)

__all__ = ["domain_intake_task", "passive_enum_task"]
__all__.append("summarize_subdomains_task")
__all__.append("validate_subdomains_task")
