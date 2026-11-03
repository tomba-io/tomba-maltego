"""
Email Count: how many addresses Tomba has for a domain, by type, department and seniority.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, to_domain


@registry.register_transform(
    display_name="Tomba - Email Count",
    input_entity="maltego.Domain",
    description="Count the email addresses Tomba has for a domain, by type, department and seniority.",
    output_entities=["maltego.Phrase"],
    disclaimer=DISCLAIMER,
)
class EmailCount(BaseTombaTransform):
    """Email Count on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        data = client.email_count(domain).get("data") or {}
        total = data.get("total", 0)

        entity = response.addEntity("maltego.Phrase", f"{domain}: {total} email addresses")
        entity.addProperty("tomba.total", displayName="Total", value=str(total))
        for key, label in (("personal_emails", "Personal"), ("generic_emails", "Generic")):
            if data.get(key) is not None:
                entity.addProperty(f"tomba.{key}", displayName=label, value=str(data[key]))
        for group in ("department", "seniority"):
            for name, count in sorted((data.get(group) or {}).items()):
                if count:
                    entity.addProperty(f"tomba.{group}.{name}",
                                       displayName=f"{group.title()}: {name}", value=str(count))
        cls.inform(response, f"Tomba has {total} email addresses for {domain}.")
