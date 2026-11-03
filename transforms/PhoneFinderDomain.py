"""
Phone Finder on a Domain: the company phone number Tomba has for a domain.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, to_domain
from .PhoneFinder import add_phone_results


@registry.register_transform(
    display_name="Tomba - Phone Finder (Domain)",
    input_entity="maltego.Domain",
    description="Find the phone number associated with a domain.",
    output_entities=["maltego.PhoneNumber"],
    disclaimer=DISCLAIMER,
)
class PhoneFinderDomain(BaseTombaTransform):
    """Phone Finder on a Domain entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = to_domain(request.Value)
        add_phone_results(cls, response, client.phone_finder(domain=domain), domain)
