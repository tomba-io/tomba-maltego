"""
Author Finder: the email address of an article's author.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties


@registry.register_transform(
    display_name="Tomba - Author Finder",
    input_entity="maltego.URL",
    description="Find the email address of the author of an article URL.",
    output_entities=["maltego.EmailAddress", "maltego.Person"],
    disclaimer=DISCLAIMER,
)
class AuthorFinder(BaseTombaTransform):
    """Author Finder on a URL entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        url = request.Value.strip()
        data = client.author_finder(url).get("data") or {}
        if not data.get("email"):
            cls.inform(response, f"No author email found for {url}.")
            return

        email = cls.add_email(response, data)
        add_properties(email, data, (
            ("info.title", "Article Title"),
            ("info.publisher_name", "Publisher"),
            ("info.publish_date", "Publish Date"),
        ))
        cls.add_person(response, data.get("first_name"), data.get("last_name"),
                       data.get("full_name"), data)
        cls.inform(response, f"Found author email {data['email']}.")
