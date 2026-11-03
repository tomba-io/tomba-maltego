"""
Domain Search on a Domain entity. Same lookup as DomainSearch, which takes a Website.
"""

from extensions import DISCLAIMER, registry

from .DomainSearch import DomainSearch


@registry.register_transform(
    display_name="Tomba - Domain Search (Domain)",
    input_entity="maltego.Domain",
    description=(
        "Find the email addresses, people and company behind a domain. "
        "Optional entity properties: tomba.limit (default 10), tomba.page, "
        "tomba.department, tomba.country, tomba.min_score."
    ),
    output_entities=["maltego.EmailAddress", "maltego.Person", "maltego.Company"],
    disclaimer=DISCLAIMER,
)
class DomainSearchDomain(DomainSearch):
    """Domain Search on a Domain entity."""
