"""
Transform to find similar websites using Tomba.io API
"""
import logging
from extensions import registry
from maltego_trx.entities import Website
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Similar Websites',
    input_entity='maltego.Website',
    description='Find similar websites',
    output_entities=['maltego.Website'],
    disclaimer="Tomba.io - Similar Websites API",
)
class Similar(BaseTombaTransform):
    """Transform to find similar websites"""

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

        website = request.Value.strip().lower()
        logger.info(f"Finding similar websites for: {website}")

        result = transform.tomba_client.similar_domain(website)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result or not result["data"]:
            response.addUIMessage("❌ No similar websites found")
            return

        for site in result["data"]:
            url = site.get("website_url", "")
            name = site.get("name", "")
            if not url:
                continue
            website_entity = response.addEntity(Website, url)
            website_entity.addProperty(
                "tomba.name", displayName="Name", value=name)

        transform.add_summary_message(
            response,
            f"Found {len(result['data'])} similar websites for {website}")
