"""
Domain Suggestions: the domains of companies matching a name.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties


@registry.register_transform(
    display_name="Tomba - Domain Suggestions",
    input_entity="maltego.Company",
    description="Find the domains of up to five companies whose name matches this one. Free.",
    output_entities=["maltego.Domain"],
    disclaimer=DISCLAIMER,
)
class DomainSuggestions(BaseTombaTransform):
    """Domain Suggestions (autocomplete) on a Company entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        query = request.Value.strip()
        suggestions = client.domain_suggestions(query).get("data") or []
        count = 0
        for item in suggestions:
            domain = item.get("domain")
            if not domain:
                continue
            entity = response.addEntity("maltego.Domain", domain)
            add_properties(entity, item, (("name", "Company"), ("email_count", "Email Count")))
            count += 1
        cls.inform(response, f"Found {count} domain(s) matching '{query}'.")
