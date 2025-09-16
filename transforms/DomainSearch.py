"""
Domain Search Transform
Find all email addresses associated with a domain
"""

import logging
from extensions import registry
from maltego_trx.entities import Email, Person, Company, Domain
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from .BaseTombaTransform import BaseTombaTransform

logger = logging.getLogger(__name__)


@registry.register_transform(
    display_name='Tomba - Domain Search',
    input_entity='maltego.Website',
    description='Find all email addresses associated with a domain.',
    output_entities=['maltego.EmailAddress',
                     'maltego.Person', 'maltego.Company'],
    disclaimer="Tomba.io - Email Finder & Verifier API",

)
class DomainSearch(BaseTombaTransform):
    """Transform to discover all emails for a domain"""

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        transform = cls()

        # Initialize Tomba client
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

        domain = request.Value.strip().lower()

        # Get transform parameters
        limit = int(request.getProperty("tomba.limit") or "50")
        department = request.getProperty("tomba.department") or None
        confidence_threshold = int(request.getProperty(
            "tomba.confidence_threshold") or "0")
        include_organization = request.getProperty(
            "tomba.include_organization") != "false"

        logger.info(f"Searching emails for domain: {domain} (limit: {limit})")

        # Perform domain search
        result = transform.tomba_client.domain_search(
            domain=domain,
            limit=limit,
            department=department
        )

        # Handle API errors
        if transform.handle_api_error(response, result):
            return

        # Process results
        if "data" not in result:
            response.addUIMessage("❌ No data returned from Tomba.io API")
            return

        data = result["data"]
        organization = data.get("organization", {})
        emails = data.get("emails", [])
        meta = result.get("meta", {})

        if not emails:
            response.addUIMessage(
                f"📭 No email addresses found for domain: {domain}"
            )

            # Still create organization entity if available
            if include_organization and organization:
                transform._create_organization_entity(
                    response, domain, organization)
            return

        # Filter emails by confidence threshold
        filtered_emails = [
            email for email in emails
            if email.get("score", 0) >= confidence_threshold
        ]

        logger.info(
            f"Found {len(filtered_emails)} emails above confidence threshold {confidence_threshold}")

        # Create organization entity first
        company_entity = None
        if include_organization and organization:
            company_entity = transform._create_organization_entity(
                response, domain, organization)

        # Create email and person entities
        person_entities = {}

        for email_data in filtered_emails:
            email_address = email_data.get("email", "")
            if not email_address:
                continue

            # Create email entity
            email_entity = response.addEntity(Email, email_address)

            # Add comprehensive email properties
            transform.add_tomba_properties(email_entity, email_data)

            # Add email-specific properties
            email_type = email_data.get("type", "unknown")
            email_entity.addProperty(
                "tomba.email_type",
                displayName="Email Type",
                value=email_type.title()
            )

            # Add confidence with visual indicator
            confidence = email_data.get("score", 0)
            email_entity.addProperty(
                "tomba.confidence_visual",
                displayName="Confidence",
                value=transform.format_confidence_message(confidence)
            )

            # Create person entity if name information is available
            first_name = email_data.get("first_name", "")
            last_name = email_data.get("last_name", "")

            if first_name or last_name:
                full_name = f"{first_name} {last_name}"

                # Avoid duplicate person entities
                person_key = full_name.lower()
                if person_key not in person_entities:
                    person_entity = response.addEntity(Person, full_name)
                    person_entities[person_key] = person_entity

                    # Add person properties
                    if first_name:
                        person_entity.addProperty(
                            "person.firstnames", value=first_name)
                    if last_name:
                        person_entity.addProperty(
                            "person.lastname", value=last_name)

                    # Add professional information
                    transform._add_person_professional_info(
                        person_entity, email_data)

                    # Add social media links
                    transform._add_social_media_links(
                        person_entity, email_data)

        # Add summary information
        total_found = len(emails)
        total_displayed = len(filtered_emails)
        total_pages = meta.get("total_pages", 1)

        summary_parts = [
            f"Found {total_found} emails",
            f"displaying {total_displayed}",
        ]

        if confidence_threshold > 0:
            summary_parts.append(f"(confidence ≥ {confidence_threshold}%)")

        if total_pages > 1:
            summary_parts.append(f"({total_pages} pages available)")

        transform.add_summary_message(response, " ".join(summary_parts))

        # Add organization summary if available
        if organization:
            org_summary_parts = []

            employee_count = organization.get("employee_count")
            if employee_count:
                org_summary_parts.append(f"{employee_count:,} employees")

            founded = organization.get("founded")
            if founded:
                org_summary_parts.append(f"founded {founded}")

            industries = organization.get("industries")
            if industries:
                org_summary_parts.append(f"industry: {industries}")

            if org_summary_parts:
                transform.add_summary_message(
                    response,
                    f"Organization: {' • '.join(org_summary_parts)}"
                )

    def _create_organization_entity(self, response: MaltegoTransform, domain: str, organization: dict):
        """Create company/organization entity"""
        company_name = organization.get("organization", domain)
        company_entity = response.addEntity(Company, company_name)

        # Add organization properties
        self.add_tomba_properties(
            company_entity, organization, prefix="tomba.org")

        # Add specific company properties
        location = organization.get("location", {})
        if location:
            country = location.get("country", "")
            city = location.get("city", "")
            if country:
                company_entity.addProperty("company.country", value=country)
            if city:
                company_entity.addProperty("company.city", value=city)

        # Add social media links
        social_links = organization.get("social_links", {})
        for platform, url in social_links.items():
            if url:
                company_entity.addProperty(
                    f"tomba.{platform}",
                    displayName=platform.replace("_url", "").title(),
                    value=url
                )

        return company_entity

    def _add_person_professional_info(self, person_entity, email_data):
        """Add professional information to person entity"""
        position = email_data.get("position", "")
        if position:
            person_entity.addProperty(
                "tomba.position",
                displayName="Position",
                value=position
            )

        department = email_data.get("department", "")
        if department:
            person_entity.addProperty(
                "tomba.department",
                displayName="Department",
                value=department.title()
            )

        seniority = email_data.get("seniority", "")
        if seniority:
            person_entity.addProperty(
                "tomba.seniority",
                displayName="Seniority",
                value=seniority.title()
            )

        gender = email_data.get("gender", "")
        if gender:
            person_entity.addProperty(
                "tomba.gender",
                displayName="Gender",
                value=gender.title()
            )

        country = email_data.get("country", "")
        if country:
            person_entity.addProperty(
                "person.country",
                displayName="Country",
                value=country.upper()
            )

    def _add_social_media_links(self, person_entity, email_data):
        """Add social media links to person entity"""
        linkedin = email_data.get("linkedin", "")
        if linkedin:
            person_entity.addProperty(
                "tomba.linkedin",
                displayName="LinkedIn",
                value=linkedin
            )

        twitter = email_data.get("twitter", "")
        if twitter:
            person_entity.addProperty(
                "tomba.twitter",
                displayName="Twitter",
                value=twitter
            )

        phone_number = email_data.get("phone_number", "")
        if phone_number:
            person_entity.addProperty(
                "person.phone",
                displayName="Phone Number",
                value=phone_number
            )
