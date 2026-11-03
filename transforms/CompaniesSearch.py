"""
Companies Search (Reveal): companies matching a natural-language description.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties, get_int_property

REVEAL_FIELDS = (
    ("website_url", "Website"),
    ("description", "Description"),
    ("industry", "Industry"),
    ("company_size", "Company Size"),
    ("revenue", "Revenue"),
    ("founded", "Founded"),
    ("type", "Type"),
    ("street_address", "Street Address"),
    ("city", "City"),
    ("state", "State"),
    ("postal_code", "Postal Code"),
    ("country", "Country"),
    ("total_emails", "Email Count"),
    ("total_similar", "Similar Companies"),
    ("linkedin_url", "LinkedIn"),
    ("twitter_url", "Twitter"),
    ("facebook_url", "Facebook"),
)


@registry.register_transform(
    display_name="Tomba - Companies Search",
    input_entity="maltego.Phrase",
    description=(
        "Search Tomba's company database with a natural-language query, such as "
        "'fintech companies in France'. Returns up to 50 companies per page; "
        "set tomba.page for later pages."
    ),
    output_entities=["maltego.Company", "maltego.Website"],
    disclaimer=DISCLAIMER,
)
class CompaniesSearch(BaseTombaTransform):
    """Companies Search (/reveal/search) on a Phrase entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        query = request.Value.strip()
        body = client.companies_search(query, page=get_int_property(request, "tomba.page", 1))
        companies = (body.get("data") or {}).get("companies") or []
        meta = body.get("meta") or {}

        for company in companies:
            name = company.get("name") or company.get("website_url")
            if not name:
                continue
            entity = response.addEntity("maltego.Company", name)
            add_properties(entity, company, REVEAL_FIELDS)
            if company.get("website_url"):
                response.addEntity("maltego.Website", company["website_url"])

        summary = f"Found {len(companies)} companies for '{query}'"
        if meta.get("total") is not None:
            summary += f" ({meta['total']} in total, page {meta.get('page', 1)} of {meta.get('pages', 1)})"
        cls.inform(response, summary + ".")
