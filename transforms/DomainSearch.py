"""
Domain Search: every email address Tomba has for a domain, with the people and the company.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import (
    BaseTombaTransform,
    TombaClient,
    add_properties,
    get_int_property,
    get_str_property,
    to_domain,
)

ORGANIZATION_FIELDS = (
    ("website_url", "Website"),
    ("description", "Description"),
    ("industries", "Industry"),
    ("founded", "Founded"),
    ("company_size", "Company Size"),
    ("company_type", "Company Type"),
    ("revenue", "Revenue"),
    ("pattern", "Email Pattern"),
    ("accept_all", "Accept All"),
    ("webmail", "Webmail"),
    ("disposable", "Disposable"),
    ("keywords", "Keywords"),
    ("ranking", "Ranking"),
    ("total_similar", "Similar Companies"),
    ("location.street_address", "Street Address"),
    ("location.city", "City"),
    ("location.state", "State"),
    ("location.postal_code", "Postal Code"),
    ("location.country", "Country"),
    ("social_links.linkedin_url", "LinkedIn"),
    ("social_links.twitter_url", "Twitter"),
    ("social_links.facebook_url", "Facebook"),
    ("social_links.github_url", "GitHub"),
    ("social_links.instagram_url", "Instagram"),
    ("social_links.youtube_url", "YouTube"),
    ("whois.registrar_name", "Registrar"),
    ("whois.created_date", "Domain Created"),
    ("last_updated", "Last Updated"),
)


@registry.register_transform(
    display_name="Tomba - Domain Search",
    input_entity="maltego.Website",
    description=(
        "Find the email addresses, people and company behind a website. "
        "Optional entity properties: tomba.limit (default 10), tomba.page, "
        "tomba.department, tomba.country, tomba.min_score."
    ),
    output_entities=["maltego.EmailAddress", "maltego.Person", "maltego.Company"],
    disclaimer=DISCLAIMER,
)
class DomainSearch(BaseTombaTransform):
    """Domain Search on a Website entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        limit = get_int_property(request, "tomba.limit", 10)
        min_score = get_int_property(request, "tomba.min_score", 0)

        body = client.domain_search(
            domain,
            page=get_int_property(request, "tomba.page"),
            limit=limit,
            department=get_str_property(request, "tomba.department"),
            country=get_str_property(request, "tomba.country"),
        )
        data = body.get("data") or {}
        organization = data.get("organization") or {}
        emails = data.get("emails") or []
        meta = body.get("meta") or {}

        if organization:
            name = organization.get("organization") or domain
            company = response.addEntity("maltego.Company", name)
            add_properties(company, organization, ORGANIZATION_FIELDS)

        kept = [e for e in emails if (e.get("score") or 0) >= min_score]
        people = set()
        for email_data in kept:
            email_data = dict(email_data, website_url=email_data.get("website_url") or domain)
            cls.add_email(response, email_data)
            key = (email_data.get("first_name") or "", email_data.get("last_name") or "")
            if any(key) and key not in people:
                people.add(key)
                cls.add_person(response, key[0], key[1], email_data.get("full_name"), email_data)

        if not emails:
            cls.inform(response, f"No email addresses found for {domain}.")
            return
        summary = f"{len(kept)} of {len(emails)} addresses shown for {domain}"
        if meta.get("total") is not None:
            summary += f" ({meta['total']} in total"
            if meta.get("total_pages"):
                summary += f", page {meta.get('current', 1)} of {meta['total_pages']}"
            summary += ")"
        cls.inform(response, summary + ".")
