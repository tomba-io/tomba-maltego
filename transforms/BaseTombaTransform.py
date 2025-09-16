"""
Base transform class using the official Tomba.io Python SDK
"""

import logging
from typing import Dict, Any, Optional
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

# Import official Tomba.io SDK
from tomba.client import Client
from tomba.services.domain import Domain
from tomba.services.finder import Finder
from tomba.services.verifier import Verifier
from tomba.services.account import Account
from settings import TOMBA_API_KEY, TOMBA_SECRET_KEY
from extensions import registry
# from settings import api_key_setting, secret_key_setting
logger = logging.getLogger(__name__)


class TombaSDKWrapper:
    """Wrapper for the official Tomba.io Python SDK with error handling"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key

        # Initialize Tomba client
        self.client = Client()
        self.client.set_key(api_key).set_secret(secret_key)

        # Initialize all services
        self.domain_service = Domain(self.client)
        self.finder_service = Finder(self.client)
        self.verifier_service = Verifier(self.client)
        self.account_service = Account(self.client)

    def _handle_request(self, service_call, *args, **kwargs) -> Dict[str, Any]:
        """Execute API call with error handling"""
        try:
            result = service_call(*args, **kwargs)

            # Check if result is valid
            if isinstance(result, dict):
                # Handle API errors in response
                if 'error' in result:
                    return {"error": result['error']}

                # Success case - return the result
                return result
            else:
                # Handle non-dict responses
                return {"data": result}

        except Exception as e:
            error_msg = str(e)

            # Parse common error types
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "Invalid API credentials. Please check your API key and secret."
            elif "403" in error_msg or "Forbidden" in error_msg:
                error_msg = "API access forbidden. Please check your subscription plan."
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                error_msg = "API rate limit exceeded. Please wait before making more requests."
            elif "timeout" in error_msg.lower():
                error_msg = "Request timeout. Please try again later."
            elif "connection" in error_msg.lower():
                error_msg = "Connection error. Please check your internet connection."

            logger.error(f"Tomba API error: {error_msg}")
            return {"error": error_msg}

    def domain_search(self, domain: str, limit: int = 10, department: str = None) -> Dict[str, Any]:
        """Search for emails in a domain"""
        return self._handle_request(
            self.domain_service.domain_search,
            domain=domain,
            limit=limit,
            department=department
        )

    def email_finder(self, domain: str, first_name: str, last_name: str) -> Dict[str, Any]:
        """Find email for a specific person"""
        return self._handle_request(
            self.finder_service.email_finder,
            domain=domain,
            first_name=first_name,
            last_name=last_name
        )

    def email_verifier(self, email: str) -> Dict[str, Any]:
        """Verify email address"""
        return self._handle_request(
            self.verifier_service.email_verifier,
            email=email
        )

    def author_finder(self, url: str) -> Dict[str, Any]:
        """Find author email from URL"""
        return self.finder_service.author_finder(
            url=url
        )

    def email_enrichment(self, email: str) -> Dict[str, Any]:
        """Enrich email with additional data"""
        return self.finder_service.enrichment(
            email=email
        )

    def linkedin_finder(self, url: str) -> Dict[str, Any]:
        """Find email from LinkedIn profile"""
        return self.finder_service.linkedin_finder(
            url=url
        )

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self._handle_request(
            self.account_service.get_account
        )


@registry.register_transform(
    display_name='Tomba - Base Transform',
    input_entity='maltego.Phrase',
    description='Base class for Tomba.io transforms',
    output_entities=[],
    settings=(),
    disclaimer="Tomba.io - Email Finder & Verifier API",
)
class BaseTombaTransform(DiscoverableTransform):
    """Base class for all Tomba.io transforms using official SDK"""

    def __init__(self):
        super().__init__()
        self.tomba_client: Optional[TombaSDKWrapper] = None

    def get_api_credentials(self, request: MaltegoMsg) -> tuple:
        """Extract API credentials from request"""
        # Try transform settings first
        # api_key = request.getTransformSetting(api_key_setting.id)
        # secret_key = request.getTransformSetting(secret_key_setting.id)

        # # # Fallback to properties
        # if not api_key:
        #     api_key = request.getProperty(api_key_setting.name)
        # if not secret_key:
        #     secret_key = request.getProperty(secret_key_setting.name)

        # Check settings.py as last resort
        if not api_key:
            import os
            api_key = TOMBA_API_KEY
        if not secret_key:
            import os
            secret_key = TOMBA_SECRET_KEY

        return api_key, secret_key

    def init_tomba_client(self, request: MaltegoMsg) -> bool:
        """Initialize Tomba SDK client"""
        api_key, secret_key = self.get_api_credentials(request)

        if not api_key or not secret_key:
            return False

        try:
            self.tomba_client = TombaSDKWrapper(api_key, secret_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Tomba client: {str(e)}")
            return False

    def handle_api_error(self, response: MaltegoTransform, result: Dict[str, Any]) -> bool:
        """Handle API errors and add UI messages"""
        if "error" in result:
            error_msg = result["error"]

            # Add contextual error messages
            if "credentials" in error_msg.lower():
                response.addUIMessage(
                    "❌ Invalid Tomba.io API credentials.\n"
                    "Please check your API key and secret in transform settings.",
                    messageType="FatalError"
                )
            elif "rate limit" in error_msg.lower():
                response.addUIMessage(
                    "⚠️ API rate limit exceeded.\n"
                    "Please wait before making more requests or upgrade your plan.",
                    messageType="PartialError"
                )
            elif "forbidden" in error_msg.lower():
                response.addUIMessage(
                    "🚫 API access forbidden.\n"
                    "Please check your subscription plan or API permissions.",
                    messageType="PartialError"
                )
            elif "timeout" in error_msg.lower():
                response.addUIMessage(
                    "⏱️ Request timeout occurred.\n"
                    "Please try again later or check your connection.",
                    messageType="PartialError"
                )
            else:
                response.addUIMessage(
                    f"⚠️ Tomba.io API error: {error_msg}",
                    messageType="PartialError"
                )
            return True
        return False

    def add_tomba_properties(self, entity, data: Dict[str, Any], prefix: str = "tomba"):
        """Add comprehensive Tomba properties to entity"""

        # Standard properties
        property_mappings = {
            f"{prefix}.confidence": ("Confidence", "confidence"),
            f"{prefix}.score": ("Score", "score"),
            f"{prefix}.verification_status": ("Verification Status", ["verification", "status"]),
            f"{prefix}.verification_result": ("Result", ["verification", "result"]),
            f"{prefix}.first_name": ("First Name", "first_name"),
            f"{prefix}.last_name": ("Last Name", "last_name"),
            f"{prefix}.full_name": ("Full Name", "full_name"),
            f"{prefix}.position": ("Position", "position"),
            f"{prefix}.department": ("Department", "department"),
            f"{prefix}.company": ("Company", "company"),
            f"{prefix}.website_url": ("Website", "website_url"),
            f"{prefix}.country": ("Country", "country"),
            f"{prefix}.gender": ("Gender", "gender"),
            f"{prefix}.phone_number": ("Phone", "phone_number"),
            f"{prefix}.twitter": ("Twitter", "twitter"),
            f"{prefix}.linkedin": ("LinkedIn", "linkedin"),
            f"{prefix}.disposable": ("Disposable", "disposable"),
            f"{prefix}.webmail": ("Webmail", "webmail"),
            f"{prefix}.accept_all": ("Accept All", "accept_all"),
            f"{prefix}.regex": ("Regex Valid", "regex"),
            f"{prefix}.mx_records": ("MX Records", "mx_records"),
            f"{prefix}.smtp_server": ("SMTP Server", "smtp_server"),
            f"{prefix}.smtp_check": ("SMTP Check", "smtp_check"),
            f"{prefix}.gibberish": ("Gibberish", "gibberish"),
            f"{prefix}.type": ("Type", "type"),
            f"{prefix}.seniority": ("Seniority", "seniority"),
            f"{prefix}.last_updated": ("Last Updated", "last_updated"),
            f"{prefix}.last_seen": ("Last Seen", "last_seen"),
        }

        for prop_name, (display_name, data_key) in property_mappings.items():
            value = self._get_nested_value(data, data_key)

            if value is not None and value != "":
                # Format boolean values
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                # Format list values
                elif isinstance(value, list):
                    value = f"{len(value)} items"

                entity.addProperty(
                    prop_name,
                    displayName=display_name,
                    value=str(value)
                )

        # Add sources information
        sources = data.get("sources", [])
        if sources:
            entity.addProperty(
                f"{prefix}.sources_count",
                displayName="Sources Count",
                value=str(len(sources))
            )

            # Add first few source URLs
            source_urls = [s.get("uri", "")
                           for s in sources[:3] if s.get("uri")]
            if source_urls:
                entity.addProperty(
                    f"{prefix}.source_urls",
                    displayName="Source URLs",
                    value=", ".join(source_urls)
                )

        # Add WHOIS information if available
        whois_data = self._get_nested_value(
            data, ["whois"]) or self._get_nested_value(data, ["email", "whois"])
        if whois_data:
            registrar = whois_data.get("registrar_name", "")
            if registrar:
                entity.addProperty(
                    f"{prefix}.registrar",
                    displayName="Registrar",
                    value=registrar
                )

            created_date = whois_data.get("created_date", "")
            if created_date:
                entity.addProperty(
                    f"{prefix}.domain_created",
                    displayName="Domain Created",
                    value=created_date
                )

    def _get_nested_value(self, data: Dict[str, Any], key_path) -> Any:
        """Get nested value from dictionary using key path"""
        if isinstance(key_path, str):
            return data.get(key_path)
        elif isinstance(key_path, list):
            current = data
            for key in key_path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        return None

    def format_confidence_message(self, confidence: int) -> str:
        """Format confidence score with descriptive text"""
        if confidence >= 90:
            return f"🟢 Very High ({confidence}%)"
        elif confidence >= 75:
            return f"🟡 High ({confidence}%)"
        elif confidence >= 50:
            return f"🟠 Medium ({confidence}%)"
        elif confidence >= 25:
            return f"🔴 Low ({confidence}%)"
        else:
            return f"⚪ Very Low ({confidence}%)"

    def add_summary_message(self, response: MaltegoTransform, summary: str):
        """Add summary information message"""
        response.addUIMessage(
            f"ℹ️ {summary}",
            messageType="Inform"
        )
