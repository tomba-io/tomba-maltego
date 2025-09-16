"""
Transform to find author email address from URL using Tomba.io API
"""
import logging
from extensions import registry
from maltego_trx.entities import Email, Person
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Author Finder',
    input_entity='maltego.URL',
    description='Find author email address from article URL using Tomba.io',
    output_entities=['maltego.EmailAddress', 'maltego.Person'],
    disclaimer="Tomba.io - Email Finder & Verifier API",
)
class AuthorFinder(BaseTombaTransform):
    """Transform to find author email from article URL"""

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        transform = cls()

        if not transform.init_tomba_client(request):
            response.addUIMessage(
                "🔑 Please configure Tomba.io API credentials:\n\n"
                "In Transform settings.py, add:\n"
                "• TOMBA_API_KEY = \"ta_xx\" Your API key (starts with 'ta_')\n"
                "• TOMBA_SECRET_KEY = \"ts_xx\" Your secret key (starts with 'ts_')\n\n"
                "Get your keys from: https://app.tomba.io/api",
                messageType="FatalError"
            )
            return

        url = request.Value.strip()

        logger.info(f"Finding author for URL: {url}")

        result = transform.tomba_client.author_finder(url)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No author data found")
            return

        data = result["data"]
        emails = data.get("emails", [])

        if not emails:
            response.addUIMessage(f"📭 No author emails found for URL: {url}")
            return

        for author_data in emails:
            email = author_data.get("email", "")
            if not email:
                continue

            # Create email entity
            email_entity = response.addEntity(Email, email)
            transform.add_tomba_properties(email_entity, author_data)

            # Create person entity if name available
            first_name = author_data.get("first_name", "")
            last_name = author_data.get("last_name", "")

            if first_name or last_name:
                full_name = f"{first_name} {last_name}".strip()
                person_entity = response.addEntity(Person, full_name)

                if first_name:
                    person_entity.addProperty(
                        "person.firstnames", value=first_name)
                if last_name:
                    person_entity.addProperty(
                        "person.lastname", value=last_name)

        transform.add_summary_message(
            response, f"Found {len(emails)} author email(s)")
