"""
Email Enrichment: the person and company details Tomba has for an address.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


@registry.register_transform(
    display_name="Tomba - Email Enrichment",
    input_entity="maltego.EmailAddress",
    description="Enrich an email address with the person's name, position, company and social profiles.",
    output_entities=["maltego.EmailAddress", "maltego.Person"],
    disclaimer=DISCLAIMER,
)
class EmailEnrichment(BaseTombaTransform):
    """Email Enrichment (/enrich) on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        data = client.email_enrichment(email).get("data") or {}
        if not data.get("email"):
            cls.inform(response, f"Tomba has no data for {email}.")
            return

        cls.add_email(response, data, email)
        cls.add_person(response, data.get("first_name"), data.get("last_name"),
                       data.get("full_name"), data)
        cls.inform(response, f"Enriched {email}.")
