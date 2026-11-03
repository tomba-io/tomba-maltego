"""
Email Finder: a person's email address from their name and company domain.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import UIM_PARTIAL, MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, get_str_property, to_domain


@registry.register_transform(
    display_name="Tomba - Email Finder",
    input_entity="maltego.Person",
    description=(
        "Find a person's email address from their name and company domain. "
        "Set the domain in the tomba.domain property of the Person entity."
    ),
    output_entities=["maltego.EmailAddress"],
    disclaimer=DISCLAIMER,
)
class EmailFinder(BaseTombaTransform):
    """Email Finder on a Person entity with a tomba.domain property."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        domain = get_str_property(request, "tomba.domain", "domain", "tomba.website_url", "tomba.company_domain")
        if not domain:
            response.addUIMessage(
                "Add a tomba.domain property (for example stripe.com) to the Person entity, then run again.",
                messageType=UIM_PARTIAL,
            )
            return
        domain = to_domain(domain)

        first = get_str_property(request, "person.firstnames")
        last = get_str_property(request, "person.lastname")
        if not (first and last):
            parts = request.Value.strip().split()
            if len(parts) < 2:
                response.addUIMessage("The Person entity needs a first and last name.",
                                      messageType=UIM_PARTIAL)
                return
            first, last = parts[0], " ".join(parts[1:])

        data = client.email_finder(domain, first, last).get("data") or {}
        if not data.get("email"):
            cls.inform(response, f"No email address found for {first} {last} at {domain}.")
            return

        cls.add_email(response, data)
        cls.inform(response, f"Found {data['email']} (score {data.get('score', 0)}).")
