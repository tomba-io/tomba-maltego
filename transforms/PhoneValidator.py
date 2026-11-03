"""
Phone Validator: whether a phone number is valid, its formats, line type and carrier.
"""

from extensions import DISCLAIMER, registry
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from .base import BaseTombaTransform, TombaClient


@registry.register_transform(
    display_name="Tomba - Phone Validator",
    input_entity="maltego.PhoneNumber",
    description="Validate a phone number (international format) and get its formats, line type and carrier.",
    output_entities=["maltego.PhoneNumber"],
    disclaimer=DISCLAIMER,
)
class PhoneValidator(BaseTombaTransform):
    """Phone Validator on a PhoneNumber entity."""

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        phone = request.Value.strip()
        data = client.phone_validator(phone).get("data")
        if not isinstance(data, dict) or not data:
            entity = response.addEntity("maltego.PhoneNumber", phone)
            entity.addProperty("tomba.valid", displayName="Valid", value="No")
            cls.inform(response, f"{phone} isn't a valid phone number.")
            return

        cls.add_phone(response, data, phone)
        cls.inform(response, f"{phone}: {'valid' if data.get('valid') else 'not valid'}"
                             f" {data.get('line_type') or ''}".rstrip() + ".")
