"""
Combined Enrichment: the person and their company from one email address.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


@registry.register_transform(
    display_name="Tomba - Combined Enrichment",
    input_entity="maltego.EmailAddress",
    description="Get the person and their company from one email address.",
    output_entities=["maltego.Person", "maltego.Company", "maltego.Domain"],
    disclaimer=DISCLAIMER,
)
class CombinedEnrichment(BaseTombaTransform):
    """Combined Enrichment (/combined/find) on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        data = client.combined_enrichment(email).get("data") or {}
        person = cls.add_enriched_person(response, data.get("person") or {})
        company_data = data.get("company") or {}
        company = cls.add_enriched_company(response, company_data)
        if company_data.get("domain"):
            response.addEntity("maltego.Domain", company_data["domain"])

        if person is None and company is None:
            cls.inform(response, f"Tomba has no data for {email}.")
        else:
            cls.inform(response, f"Enriched {email}.")
