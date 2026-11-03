"""
Person Enrichment: a person's profile from their email address.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


@registry.register_transform(
    display_name="Tomba - Person Enrichment",
    input_entity="maltego.EmailAddress",
    description="Get a person's profile from their email address: name, location, employment and social handles.",
    output_entities=["maltego.Person"],
    disclaimer=DISCLAIMER,
)
class PersonEnrichment(BaseTombaTransform):
    """Person Enrichment (/people/find) on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        person = client.person_enrichment(email).get("data") or {}
        if cls.add_enriched_person(response, person) is None:
            cls.inform(response, f"Tomba has no person data for {email}.")
            return
        cls.inform(response, f"Enriched the person behind {email}.")
