"""
Similar Websites: companies similar to a website.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties, to_domain


@registry.register_transform(
    display_name="Tomba - Similar Websites",
    input_entity="maltego.Website",
    description="Find websites of companies similar to this one.",
    output_entities=["maltego.Website"],
    disclaimer=DISCLAIMER,
)
class Similar(BaseTombaTransform):
    """Similar Websites on a Website entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        sites = client.similar_websites(domain).get("data") or []
        count = 0
        for site in sites:
            url = site.get("website_url")
            if not url:
                continue
            entity = response.addEntity("maltego.Website", url)
            add_properties(entity, site, (("name", "Company"), ("industries", "Industry")))
            count += 1
        cls.inform(response, f"Found {count} similar website(s) for {domain}.")
