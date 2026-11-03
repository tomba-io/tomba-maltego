"""
Company Enrichment: a company's profile from its domain.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, to_domain


@registry.register_transform(
    display_name="Tomba - Company Enrichment",
    input_entity="maltego.Domain",
    description="Get a company's profile from its domain: industry, size, revenue, location and social handles.",
    output_entities=["maltego.Company"],
    disclaimer=DISCLAIMER,
)
class CompanyEnrichment(BaseTombaTransform):
    """Company Enrichment (/companies/find) on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        company = client.company_enrichment(domain).get("data") or {}
        if cls.add_enriched_company(response, company) is None:
            cls.inform(response, f"Tomba has no company data for {domain}.")
            return
        cls.inform(response, f"Enriched the company behind {domain}.")
