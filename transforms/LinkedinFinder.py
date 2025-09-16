
import logging
from extensions import registry
from maltego_trx.entities import Email, Person
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - LinkedIn Finder',
    input_entity='maltego.URL',
    description='Find email address from LinkedIn profile.',
    output_entities=['maltego.EmailAddress', 'maltego.Person'],
    disclaimer="Tomba.io - Email Finder & Verifier API",

)
class LinkedinFinder(BaseTombaTransform):
    """Transform to find email from LinkedIn profile"""

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

        linkedin_url = request.Value.strip()

        logger.info(f"Finding email from LinkedIn: {linkedin_url}")

        result = transform.tomba_client.linkedin_finder(linkedin_url)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No LinkedIn data found")
            return

        data = result["data"]
        email = data.get("email", "")

        if not email:
            response.addUIMessage("📭 No email found for LinkedIn profile")
            return

        # Create email entity
        email_entity = response.addEntity(Email, email)
        transform.add_tomba_properties(email_entity, data)

        # Create person entity
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        if first_name or last_name:
            full_name = f"{first_name} {last_name}".strip()
            person_entity = response.addEntity(Person, full_name)
            person_entity.addProperty(
                "tomba.linkedin", displayName="LinkedIn", value=linkedin_url)

        transform.add_summary_message(
            response, f"Found email {email} for LinkedIn profile")
