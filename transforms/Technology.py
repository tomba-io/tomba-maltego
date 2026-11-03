"""
Technology: the technologies a domain's website uses.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties, to_domain


@registry.register_transform(
    display_name="Tomba - Technology",
    input_entity="maltego.Domain",
    description="List the technologies a domain's website uses, one Phrase entity per technology.",
    output_entities=["maltego.Phrase"],
    disclaimer=DISCLAIMER,
)
class Technology(BaseTombaTransform):
    """Technology lookup on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        techs = client.technology_lookup(domain).get("data") or []
        for tech in techs:
            name = tech.get("name")
            if not name:
                continue
            entity = response.addEntity("maltego.Phrase", name)
            add_properties(entity, tech, (
                ("slug", "Slug"),
                ("website", "Website"),
                ("description", "Description"),
            ))
            categories = tech.get("categories") or []
            if isinstance(categories, dict):
                categories = [categories]
            names = [c.get("name") for c in categories if isinstance(c, dict) and c.get("name")]
            if names:
                entity.addProperty("tomba.categories", displayName="Categories", value=", ".join(names))
        cls.inform(response, f"Found {len(techs)} technolog{'y' if len(techs) == 1 else 'ies'} on {domain}.")
