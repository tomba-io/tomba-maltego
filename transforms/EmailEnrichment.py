"""
T
"""
import logging
from extensions import registry
from maltego_trx.entities import Email, Person
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Email Enrichment',
    input_entity='maltego.EmailAddress',
    description='Enrich an email address with additional data.',
    output_entities=['maltego.EmailAddress', 'maltego.Person'],
    disclaimer="Tomba.io - Email Finder & Verifier API",
)
class EmailEnrichment(BaseTombaTransform):
    """Transform to enrich email with additional data"""

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

        email = request.Value.strip().lower()

        logger.info(f"Enriching email: {email}")

        result = transform.tomba_client.email_enrichment(email)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No enrichment data available")
            return

        data = result["data"]

        # Create enriched email entity
        enriched_email = response.addEntity(Email, email)
        transform.add_tomba_properties(enriched_email, data)

        # Create person entity if available
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        if first_name or last_name:
            full_name = f"{first_name} {last_name}".strip()
            person_entity = response.addEntity(Person, full_name)

            # Add enriched person data
            for prop, value in data.items():
                if prop in ["position", "company", "linkedin", "twitter"] and value:
                    person_entity.addProperty(
                        f"tomba.{prop}", displayName=prop.title(), value=value)

        transform.add_summary_message(
            response, "Email successfully enriched with additional data")
