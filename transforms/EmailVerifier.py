"""
Transform to verify email address deliverability using Tomba.io API
"""
import logging
from extensions import registry

from maltego_trx.entities import Email
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Email Verifier',
    input_entity='maltego.EmailAddress',
    description='Verify email address deliverability',
    output_entities=['maltego.EmailAddress'],
    disclaimer="Tomba.io - Email Finder & Verifier API",

)
class EmailVerifier(BaseTombaTransform):
    """Transform to verify email address deliverability"""

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

        logger.info(f"Verifying email: {email}")

        result = transform.tomba_client.email_verifier(email)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result:
            response.addUIMessage("❌ No verification data returned")
            return

        data = result["data"]
        email_data = data.get("email", {})

        # Create enhanced email entity
        verified_email = response.addEntity(Email, email)

        # Add verification properties
        transform.add_tomba_properties(verified_email, email_data)

        # Add verification-specific properties
        status = email_data.get("status", "unknown")
        result_status = email_data.get("result", "unknown")
        score = email_data.get("score", 0)

        verified_email.addProperty(
            "tomba.verification_status", displayName="Status", value=status.title())
        verified_email.addProperty(
            "tomba.verification_result", displayName="Result", value=result_status.title())
        verified_email.addProperty(
            "tomba.verification_score", displayName="Score", value=f"{score}%")

        # Technical verification details
        checks = {
            "mx_records": "MX Records",
            "smtp_server": "SMTP Server",
            "smtp_check": "SMTP Check",
            "regex": "Syntax Valid",
            "disposable": "Disposable",
            "webmail": "Webmail",
            "gibberish": "Gibberish",
            "accept_all": "Accept All",
            "block": "Blocked"
        }

        for key, label in checks.items():
            value = email_data.get(key)
            if value is not None:
                display_value = "Yes" if value else "No"
                verified_email.addProperty(
                    f"tomba.{key}", displayName=label, value=display_value)

        # Add status indicator
        status_emoji = {"valid": "✅", "invalid": "❌",
                        "risky": "⚠️", "unknown": "❓"}
        emoji = status_emoji.get(status, "❓")

        transform.add_summary_message(
            response, f"{emoji} {status.title()} - {result_status.title()} ({score}%)")
