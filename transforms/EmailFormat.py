"""
Email Format: the address patterns a domain uses.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, to_domain


@registry.register_transform(
    display_name="Tomba - Email Format",
    input_entity="maltego.Domain",
    description="List the email address patterns a domain uses, such as {first}.{last}, with their share.",
    output_entities=["maltego.Phrase"],
    disclaimer=DISCLAIMER,
)
class EmailFormat(BaseTombaTransform):
    """Email Format on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        formats = client.email_format(domain).get("data") or []
        for item in formats:
            pattern = item.get("format")
            if not pattern:
                continue
            entity = response.addEntity("maltego.Phrase", f"{pattern}@{domain}")
            entity.addProperty("tomba.format", displayName="Format", value=pattern)
            if item.get("percentage") is not None:
                entity.addProperty("tomba.percentage", displayName="Percentage",
                                   value=f"{item['percentage']}%")
        if not formats:
            cls.inform(response, f"No email format known for {domain}.")
        else:
            cls.inform(response, f"Found {len(formats)} email format(s) for {domain}.")
