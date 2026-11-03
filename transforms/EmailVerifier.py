"""
Email Verifier: check whether an address is deliverable.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient, add_properties

VERIFIER_FIELDS = (
    ("status", "Status"),
    ("result", "Result"),
    ("score", "Score"),
    ("smtp_provider", "SMTP Provider"),
    ("mx.records", "MX Records"),
    ("mx_check", "MX Check"),
    ("smtp_server", "SMTP Server"),
    ("smtp_check", "SMTP Check"),
    ("accept_all", "Accept All"),
    ("greylisted", "Greylisted"),
    ("block", "Blocked"),
    ("gibberish", "Gibberish"),
    ("disposable", "Disposable"),
    ("webmail", "Webmail"),
    ("regex", "Valid Syntax"),
    ("whois.registrar_name", "Registrar"),
    ("whois.created_date", "Domain Created"),
)


@registry.register_transform(
    display_name="Tomba - Email Verifier",
    input_entity="maltego.EmailAddress",
    description="Verify an email address: status, deliverability, SMTP and MX checks.",
    output_entities=["maltego.EmailAddress"],
    disclaimer=DISCLAIMER,
)
class EmailVerifier(BaseTombaTransform):
    """Email Verifier on an EmailAddress entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        email = request.Value.strip().lower()
        body = client.email_verifier(email)
        data = body.get("data") or {}
        result = data.get("email") or {}

        entity = response.addEntity("maltego.EmailAddress", email)
        add_properties(entity, result, VERIFIER_FIELDS, prefix="tomba.verifier")
        sources = data.get("sources") or []
        if sources:
            entity.addProperty("tomba.sources_count", displayName="Sources", value=str(len(sources)))

        cls.inform(response, f"{email}: {result.get('status', 'unknown')} "
                             f"({result.get('result', 'unknown')}, score {result.get('score', 0)}).")
