"""
Phone Finder: phone numbers Tomba has for an email address.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


def add_phone_results(transform, response: MaltegoTransform, body: dict, subject: str) -> None:
    data = body.get("data")
    rows = data if isinstance(data, list) else [data] if data else []
    added = [transform.add_phone(response, row) for row in rows if isinstance(row, dict)]
    added = [a for a in added if a is not None]
    if added:
        transform.inform(response, f"Found {len(added)} phone number(s) for {subject}.")
    else:
        transform.inform(response, f"No phone number found for {subject}.")


@registry.register_transform(
    display_name="Tomba - Phone Finder",
    input_entity="maltego.EmailAddress",
    description="Find the phone number associated with an email address.",
    output_entities=["maltego.PhoneNumber"],
    disclaimer=DISCLAIMER,
)
class PhoneFinder(BaseTombaTransform):
    """Phone Finder on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        add_phone_results(cls, response, client.phone_finder(email=email), email)
