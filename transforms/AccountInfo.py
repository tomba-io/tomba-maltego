import logging
from extensions import registry
from maltego_trx.entities import Phrase
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Account Info',
    input_entity='maltego.Phrase',
    description='Get Tomba.io account information',
    output_entities=['maltego.Phrase'],
    disclaimer="Tomba.io - Email Finder & Verifier API",
)
class AccountInfo(BaseTombaTransform):
    """Transform to get Tomba.io account information"""

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

        logger.info("Retrieving account information")

        result = transform.tomba_client.get_account_info()

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No account data available")
            return

        data = result["data"]

        # Create account info entity
        account_info = f"Tomba Account: {data.get('email', 'Unknown')}"
        account_entity = response.addEntity(Phrase, account_info)

        # Add account properties
        for key, value in data.items():
            if value is not None:
                account_entity.addProperty(
                    f"tomba.account.{key}", displayName=key.title(), value=str(value))

        # Add usage information if available
        pricing = data.get("pricing", {})
        if pricing:
            for key, value in pricing.items():
                account_entity.addProperty(
                    f"tomba.usage.{key}", displayName=f"Usage {key.title()}", value=str(value))

        transform.add_summary_message(
            response, f"Account: {data.get('email', 'Unknown')} - Plan: {data.get('plan', 'Unknown')}")
