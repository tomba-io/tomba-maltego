"""
Email Sources: the web pages where Tomba found an email address.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties


@registry.register_transform(
    display_name="Tomba - Email Sources",
    input_entity="maltego.EmailAddress",
    description="List the web pages where Tomba found an email address.",
    output_entities=["maltego.URL"],
    disclaimer=DISCLAIMER,
)
class EmailSources(BaseTombaTransform):
    """Email Sources on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        sources = client.email_sources(email).get("data") or []
        count = 0
        for source in sources:
            uri = source.get("uri")
            if not uri:
                continue
            entity = response.addEntity("maltego.URL", uri)
            entity.addProperty("url", displayName="URL", value=uri)
            add_properties(entity, source, (
                ("website_url", "Website"),
                ("extracted_on", "Extracted On"),
                ("last_seen_on", "Last Seen On"),
                ("still_on_page", "Still On Page"),
            ))
            count += 1
        cls.inform(response, f"Found {count} source(s) for {email}.")
