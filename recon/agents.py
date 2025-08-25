from __future__ import annotations

import os

from crewai import Agent
from langchain_openai import ChatOpenAI

from recon.tools.amass_tool import amass_passive_enum

llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mint"))

passive_recon_agent = Agent(
    role="Passive Recon Agent",
    goal="Safely enumerate subdomains for {target_domain} using only passive sources.",
    backstory=(
        "A compliance-first OSINT specialist working strictly within authorized "
        "bug-bounty scope. Prioritizes privacy, legality, and reproducibility; "
        "never performs active probing."
    ),
    tools=[amass_passive_enum],
    allow_delegation=False,
    verbose=True,
    llm=llm,
)

__all__ = ["passive_recon_agent"]
