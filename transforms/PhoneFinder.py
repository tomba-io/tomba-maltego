"""
Transform to find phone number details using Tomba.io API
"""
import logging
from extensions import registry

from maltego_trx.entities import Email
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Phone Finder',
    input_entity='maltego.EmailAddress',
    description='Find phone number details',
    output_entities=['maltego.PhoneNumber'],
    disclaimer="Tomba.io - Phone Finder API",

)
class PhoneFinder(BaseTombaTransform):
    """Transform to find phone number details"""

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

        logger.info(f"Verifying email address: {email}")

        result = transform.tomba_client.phone_finder(email)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No verification data returned")
            return

        data = result["data"]
        phone_data = data

        # Create enhanced phone entity
        verified_phone = response.addEntity(Email, email)

        # Add verification properties
        transform.add_tomba_properties(verified_phone, phone_data)

        # Add verification-specific properties based on new response
        valid = phone_data.get("valid", False)
        verified_phone.addProperty(
            "tomba.valid", displayName="Valid", value="Yes" if valid else "No")
        verified_phone.addProperty(
            "tomba.local_format", displayName="Local Format", value=phone_data.get("local_format", ""))
        verified_phone.addProperty(
            "tomba.intl_format", displayName="International Format", value=phone_data.get("intl_format", ""))
        verified_phone.addProperty(
            "tomba.e164_format", displayName="E.164 Format", value=phone_data.get("e164_format", ""))
        verified_phone.addProperty(
            "tomba.rfc3966_format", displayName="RFC3966 Format", value=phone_data.get("rfc3966_format", ""))
        verified_phone.addProperty(
            "tomba.country_code", displayName="Country Code", value=phone_data.get("country_code", ""))
        verified_phone.addProperty(
            "tomba.line_type", displayName="Line Type", value=phone_data.get("line_type", ""))
        verified_phone.addProperty(
            "tomba.timezones", displayName="Timezones", value=phone_data.get("timezones", ""))

        # Carrier details (if available)
        carrier = phone_data.get("carrier", {})
        if carrier:
            for k, v in carrier.items():
                verified_phone.addProperty(
                    f"tomba.carrier_{k}", displayName=f"Carrier {k.title()}", value=str(v))

        # Add status indicator
        status_emoji = {True: "✅", False: "❌"}
        emoji = status_emoji.get(valid, "❓")
        transform.add_summary_message(
            response,
            f"{emoji} {'Valid' if valid else 'Invalid'} - {phone_data.get('intl_format', email)}")
