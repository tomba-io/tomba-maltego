"""
Transform to find technologies used by a domain using Tomba.io API
"""
import logging
from extensions import registry
from maltego_trx.entities import Domain
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Technology',
    input_entity='maltego.Domain',
    description='Find technologies used by a domain',
    output_entities=['maltego.Domain'],
    disclaimer="Tomba.io - Technology API",
)
class Technology(BaseTombaTransform):
    """Transform to find technologies used by a domain"""

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

        domain = request.Value.strip().lower()
        logger.info(f"Finding technologies for domain: {domain}")

        result = transform.tomba_client.technology_lookup(domain)

        if transform.handle_api_error(response, result):
            return

        if "data" not in result or not result["data"]:
            response.addUIMessage("❌ No technology data found")
            return

        for tech in result["data"]:
            tech_name = tech.get("name", "")
            tech_slug = tech.get("slug", "")
            tech_icon = tech.get("icon", "")
            tech_website = tech.get("website", "")
            categories = tech.get("categories", {})
            category_name = categories.get("name", "")
            category_slug = categories.get("slug", "")
            category_id = categories.get("id", "")

            # Add technology as a property to the domain entity
            tech_entity = response.addEntity(Domain, domain)
            tech_entity.addProperty(
                "tomba.technology_name", displayName="Technology Name", value=tech_name)
            tech_entity.addProperty(
                "tomba.technology_slug", displayName="Technology Slug", value=tech_slug)
            tech_entity.addProperty(
                "tomba.technology_icon", displayName="Technology Icon", value=tech_icon)
            tech_entity.addProperty(
                "tomba.technology_website", displayName="Technology Website", value=tech_website)
            tech_entity.addProperty(
                "tomba.category_name", displayName="Category Name", value=category_name)
            tech_entity.addProperty(
                "tomba.category_slug", displayName="Category Slug", value=category_slug)
            tech_entity.addProperty(
                "tomba.category_id", displayName="Category ID", value=str(category_id))

        transform.add_summary_message(
            response,
            f"Found {len(result['data'])} technologies for domain {domain}")
