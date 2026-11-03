"""
Domain Status: whether a domain is a webmail or disposable email provider.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, format_value, to_domain


@registry.register_transform(
    display_name="Tomba - Domain Status",
    input_entity="maltego.Domain",
    description="Check whether a domain is a webmail or disposable email provider. Free.",
    output_entities=["maltego.Domain"],
    disclaimer=DISCLAIMER,
)
class DomainStatus(BaseTombaTransform):
    """Domain Status on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        body = client.domain_status(domain)
        # This endpoint has no "data" envelope.
        status = body.get("data") if isinstance(body.get("data"), dict) else body

        entity = response.addEntity("maltego.Domain", domain)
        for key, label in (("webmail", "Webmail"), ("disposable", "Disposable")):
            value = format_value(status.get(key))
            if value is not None:
                entity.addProperty(f"tomba.{key}", displayName=label, value=value)
        cls.inform(response, f"{domain}: webmail {format_value(status.get('webmail')) or '?'}, "
                             f"disposable {format_value(status.get('disposable')) or '?'}.")
