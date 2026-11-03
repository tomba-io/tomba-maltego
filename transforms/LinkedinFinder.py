"""
LinkedIn Finder: the email address behind a LinkedIn profile URL.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


@registry.register_transform(
    display_name="Tomba - LinkedIn Finder",
    input_entity="maltego.URL",
    description="Find the email address of the person behind a LinkedIn profile URL.",
    output_entities=["maltego.EmailAddress", "maltego.Person"],
    disclaimer=DISCLAIMER,
)
class LinkedinFinder(BaseTombaTransform):
    """LinkedIn Finder on a URL entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        url = request.Value.strip()
        data = client.linkedin_finder(url).get("data") or {}
        if isinstance(data, list):
            data = data[0] if data else {}
        if not data.get("email"):
            cls.inform(response, f"No email found for {url}.")
            return

        cls.add_email(response, data)
        person = cls.add_person(response, data.get("first_name"), data.get("last_name"),
                                data.get("full_name"), data)
        if person is not None and not data.get("linkedin"):
            person.addProperty("tomba.linkedin", displayName="LinkedIn", value=url)
        cls.inform(response, f"Found {data['email']} for this profile.")
