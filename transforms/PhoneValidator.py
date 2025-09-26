"""
Transform to validate phone number using Tomba.io API
"""
import logging
from extensions import registry
from maltego_trx.entities import PhoneNumber
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Phone Validator',
    input_entity='maltego.PhoneNumber',
    description='Validate phone number',
    output_entities=['maltego.PhoneNumber'],
    disclaimer="Tomba.io - Phone Validator API",
)
class PhoneValidator(BaseTombaTransform):
    """Transform to validate phone number"""

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        transform = cls()

        if not transform.init_tomba_client(request):
            response.addUIMessage(
                "🔑 Please configure Tomba.io API credentials:\n\n"
                "In Transform settings.py, add:\n"
                "• TOMBA_API_KEY = 'ta_xx' Your API key (starts with 'ta_')\n"
                "• TOMBA_SECRET_KEY = 'ts_xx' Your secret key (starts with 'ts_')\n\n"
                "Get your keys from: https://app.tomba.io/api",
                messageType="FatalError"
            )
            return

        phone = request.Value.strip().lower()
        logger.info(f"Validating phone number: {phone}")

        result = transform.tomba_client.phone_validator(phone)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No validation data returned")
            return

        data = result["data"]

        # Create phone entity
        validated_phone = response.addEntity(PhoneNumber, phone)

        # Add validation properties
        valid = data.get("valid", False)
        validated_phone.addProperty(
            "tomba.valid", displayName="Valid", value="Yes" if valid else "No")
        validated_phone.addProperty(
            "tomba.local_format", displayName="Local Format", value=data.get("local_format", ""))
        validated_phone.addProperty(
            "tomba.intl_format", displayName="International Format", value=data.get("intl_format", ""))
        validated_phone.addProperty(
            "tomba.e164_format", displayName="E.164 Format", value=data.get("e164_format", ""))
        validated_phone.addProperty(
            "tomba.rfc3966_format", displayName="RFC3966 Format", value=data.get("rfc3966_format", ""))
        validated_phone.addProperty(
            "tomba.country_code", displayName="Country Code", value=data.get("country_code", ""))
        validated_phone.addProperty(
            "tomba.line_type", displayName="Line Type", value=data.get("line_type", ""))
        validated_phone.addProperty(
            "tomba.timezones", displayName="Timezones", value=data.get("timezones", ""))

        # Carrier details (if available)
        carrier = data.get("carrier", {})
        if carrier:
            for k, v in carrier.items():
                validated_phone.addProperty(
                    f"tomba.carrier_{k}", displayName=f"Carrier {k.title()}", value=str(v))

        # Add status indicator
        status_emoji = {True: "✅", False: "❌"}
        emoji = status_emoji.get(valid, "❓")
        transform.add_summary_message(
            response,
            f"{emoji} {'Valid' if valid else 'Invalid'} - {data.get('intl_format', phone)}")
