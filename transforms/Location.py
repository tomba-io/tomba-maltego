"""
Location: the countries of the people Tomba has addresses for at a domain.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, to_domain


@registry.register_transform(
    display_name="Tomba - Location",
    input_entity="maltego.Domain",
    description="Break down a domain's email addresses by country, one Location entity per country.",
    output_entities=["maltego.Location"],
    disclaimer=DISCLAIMER,
)
class Location(BaseTombaTransform):
    """Location breakdown on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        rows = client.location(domain).get("data") or []
        for row in rows:
            code = row.get("name")
            if not code:
                continue
            entity = response.addEntity("maltego.Location", code)
            entity.addProperty("countrycode", displayName="Country Code", value=code)
            entity.addProperty("tomba.total", displayName="Addresses", value=str(row.get("total", 0)))
        cls.inform(response, f"Found addresses in {len(rows)} countr{'y' if len(rows) == 1 else 'ies'} for {domain}.")
