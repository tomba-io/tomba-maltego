"""
Shared plumbing for the Tomba Maltego transforms.

Every transform subclasses ``BaseTombaTransform`` and implements ``run()``.
The base class loads credentials, builds the SDK client, and turns SDK and
API errors into Maltego UI messages, so a transform only maps a response
body onto entities.
"""

import logging
import os
import re
from typing import Any, Dict, Iterable, Optional, Tuple

from maltego_trx.maltego import (
    UIM_FATAL,
    UIM_INFORM,
    UIM_PARTIAL,
    MaltegoEntity,
    MaltegoMsg,
    MaltegoTransform,
)
from maltego_trx.transform import DiscoverableTransform
from tomba import (
    Client,
    Count,
    Domain,
    Enrichment,
    Finder,
    Phone,
    Reveal,
    Similar,
    Sources,
    Status,
    Technology,
    TombaException,
    Verifier,
)

logger = logging.getLogger(__name__)

CREDENTIALS_MESSAGE = (
    "Tomba API credentials are missing.\n\n"
    "Set TOMBA_API_KEY (starts with 'ta_') and TOMBA_SECRET_KEY (starts with 'ts_') "
    "as environment variables, or in settings.py next to project.py "
    "(copy settings.py.template).\n\n"
    "Get your key and secret at https://app.tomba.io/api"
)


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Read the API key and secret: environment variables first, then settings.py."""
    api_key = os.environ.get("TOMBA_API_KEY")
    secret_key = os.environ.get("TOMBA_SECRET_KEY")

    if not (api_key and secret_key):
        try:
            import settings  # optional local file, gitignored
        except ImportError:
            settings = None
        if settings is not None:
            api_key = api_key or getattr(settings, "TOMBA_API_KEY", None)
            secret_key = secret_key or getattr(settings, "TOMBA_SECRET_KEY", None)

    placeholders = ("ta_xxxxxxxxxxxxxxxxxxxx", "ts_xxxxxxxxxxxxxxxxxxxx")
    if api_key in placeholders or secret_key in placeholders:
        return None, None
    return api_key or None, secret_key or None


class TombaError(Exception):
    """An API or SDK failure, already phrased for the Maltego UI."""

    def __init__(self, message: str, message_type: str = UIM_PARTIAL):
        super().__init__(message)
        self.message = message
        self.message_type = message_type


class NotFound(TombaError):
    """The API answered, but has no data for the input."""

    def __init__(self, message: str):
        super().__init__(message, UIM_INFORM)


def _friendly_error(code: int, message: str) -> TombaError:
    if code == 401:
        return TombaError(
            "Invalid Tomba API credentials. Check TOMBA_API_KEY and TOMBA_SECRET_KEY.",
            UIM_FATAL,
        )
    if code == 402:
        return TombaError("Not enough Tomba credits for this request. See https://app.tomba.io/pricing")
    if code == 403:
        return TombaError(f"Tomba API access forbidden: {message}")
    if code == 404:
        return NotFound(f"Tomba has no data for this input: {message}")
    if code == 429:
        return TombaError("Tomba rate limit reached. Wait before running more transforms.")
    if code == 0 and "timed out" in str(message).lower():
        return TombaError("The Tomba API request timed out. Try again later.")
    if code == 0:
        return TombaError(f"Couldn't reach the Tomba API: {message}")
    return TombaError(f"Tomba API error ({code}): {message}")


class TombaClient:
    """Thin wrapper around the official SDK that returns the API body or raises TombaError."""

    def __init__(self, api_key: str, secret_key: str):
        self.client = Client()
        self.client.set_key(api_key).set_secret(secret_key)

        self.count = Count(self.client)
        self.domain = Domain(self.client)
        self.enrichment = Enrichment(self.client)
        self.finder = Finder(self.client)
        self.phone = Phone(self.client)
        self.reveal = Reveal(self.client)
        self.similar = Similar(self.client)
        self.sources = Sources(self.client)
        self.status = Status(self.client)
        self.technology = Technology(self.client)
        self.verifier = Verifier(self.client)

    @classmethod
    def from_settings(cls) -> Optional["TombaClient"]:
        api_key, secret_key = get_credentials()
        if not (api_key and secret_key):
            return None
        return cls(api_key, secret_key)

    @staticmethod
    def call(method, *args, **kwargs) -> Dict[str, Any]:
        """Run an SDK method and return the decoded API body.

        The SDK returns ``{"data": <body>, "rate_limit": {...}}`` and raises
        ``TombaException`` for HTTP errors. Some endpoints (Enrichment) answer
        200 with an ``errors`` object, which is raised here too.
        """
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        try:
            result = method(*args, **kwargs)
        except TombaException as e:
            logger.error("Tomba API error %s: %s", e.code, e.message)
            raise _friendly_error(int(e.code or 0), str(e.message)) from e

        body = result.get("data") if isinstance(result, dict) and "rate_limit" in result else result
        if not isinstance(body, dict):
            return {"data": body}

        errors = body.get("errors")
        if errors:
            code = int(errors.get("code") or 0) if isinstance(errors, dict) else 0
            message = errors.get("message", str(errors)) if isinstance(errors, dict) else str(errors)
            if code == 404 or (isinstance(errors, dict) and errors.get("type") == "not_found"):
                raise NotFound(message)
            raise _friendly_error(code, message)
        return body

    # Finder
    def domain_search(self, domain, page=None, limit=None, department=None, country=None):
        return self.call(
            self.domain.domain_search, domain,
            page=page, limit=limit, department=department, country=country,
        )

    def email_finder(self, domain, first_name, last_name):
        return self.call(self.finder.email_finder, domain, first_name, last_name)

    def author_finder(self, url):
        return self.call(self.finder.author_finder, url)

    def linkedin_finder(self, url):
        return self.call(self.finder.linkedin_finder, url)

    def email_enrichment(self, email):
        return self.call(self.finder.enrichment, email)

    def email_format(self, domain):
        return self.call(self.finder.format, domain)

    def location(self, domain):
        return self.call(self.finder.location, domain)

    def email_count(self, domain):
        return self.call(self.count.email_count, domain)

    # Email
    def email_verifier(self, email):
        return self.call(self.verifier.email_verifier, email)

    def email_sources(self, email):
        return self.call(self.sources.email_sources, email)

    # Enrichment
    def person_enrichment(self, email):
        return self.call(self.enrichment.person, email)

    def company_enrichment(self, domain):
        return self.call(self.enrichment.company, domain)

    def combined_enrichment(self, email):
        return self.call(self.enrichment.combined, email)

    # Phone
    def phone_finder(self, email=None, domain=None, linkedin=None):
        return self.call(self.phone.finder, email=email, domain=domain, linkedin=linkedin)

    def phone_validator(self, phone):
        return self.call(self.phone.validator, phone)

    # Domain
    def domain_status(self, domain):
        return self.call(self.status.domain_status, domain)

    def domain_suggestions(self, query):
        return self.call(self.status.auto_complete, query)

    def similar_websites(self, domain):
        return self.call(self.similar.websites, domain)

    def technology_lookup(self, domain):
        return self.call(self.technology.list, domain)

    # Reveal
    def companies_search(self, query, page=None):
        return self.call(self.reveal.search_companies, query=query, page=page)


# --------------------------------------------------------------------------
# Input helpers
# --------------------------------------------------------------------------

_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def to_domain(value: str) -> str:
    """Normalize a Website/Domain/URL value to a bare domain: 'https://www.Stripe.com/x' -> 'stripe.com'."""
    value = (value or "").strip().lower()
    value = _SCHEME.sub("", value)
    value = value.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    value = value.rsplit("@", 1)[-1].split(":", 1)[0]
    if value.startswith("www."):
        value = value[4:]
    return value


def get_int_property(request: MaltegoMsg, name: str, default: Optional[int] = None) -> Optional[int]:
    raw = request.getProperty(name)
    if raw in (None, ""):
        return default
    try:
        return int(str(raw).strip())
    except ValueError:
        return default


def get_str_property(request: MaltegoMsg, *names: str) -> Optional[str]:
    for name in names:
        raw = request.getProperty(name)
        if raw not in (None, ""):
            return str(raw).strip()
    return None


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def format_value(value: Any) -> Optional[str]:
    """Render an API value as a property string, or None to skip it."""
    if value is None or value == "" or value == [] or value == {}:
        return None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple)):
        items = [format_value(v) for v in value if not isinstance(v, dict)]
        items = [i for i in items if i]
        return ", ".join(items) if items else None
    if isinstance(value, dict):
        return None
    return str(value)


def get_path(data: Any, path: str) -> Any:
    """Read 'a.b.c' from nested dicts, returning None when a key is missing."""
    current = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def add_properties(entity: MaltegoEntity, data: Dict[str, Any],
                   fields: Iterable[Tuple[str, str]], prefix: str = "tomba") -> None:
    """Add one property per (path, display name) pair that has a value.

    The property name is ``<prefix>.<path with dots replaced by underscores>``.
    """
    for path, display in fields:
        value = format_value(get_path(data, path))
        if value is not None:
            name = path.replace(".", "_")
            entity.addProperty(f"{prefix}.{name}", displayName=display, value=value)


EMAIL_FIELDS = (
    ("score", "Score"),
    ("type", "Email Type"),
    ("first_name", "First Name"),
    ("last_name", "Last Name"),
    ("full_name", "Full Name"),
    ("position", "Position"),
    ("department", "Department"),
    ("seniority", "Seniority"),
    ("company", "Company"),
    ("website_url", "Website"),
    ("country", "Country"),
    ("gender", "Gender"),
    ("pattern", "Pattern"),
    ("linkedin", "LinkedIn"),
    ("twitter", "Twitter"),
    ("phone_number", "Phone Number"),
    ("accept_all", "Accept All"),
    ("disposable", "Disposable"),
    ("webmail", "Webmail"),
    ("verification.status", "Verification Status"),
    ("verification.date", "Verification Date"),
)

ENRICHED_PERSON_FIELDS = (
    ("email", "Email"),
    ("gender", "Gender"),
    ("location", "Location"),
    ("geo.city", "City"),
    ("geo.state", "State"),
    ("geo.country", "Country"),
    ("bio", "Bio"),
    ("site", "Site"),
    ("avatar", "Avatar"),
    ("employment.name", "Company"),
    ("employment.domain", "Company Domain"),
    ("employment.title", "Title"),
    ("employment.role", "Role"),
    ("employment.seniority", "Seniority"),
    ("linkedin.handle", "LinkedIn"),
    ("twitter.handle", "Twitter"),
    ("github.handle", "GitHub"),
    ("facebook.handle", "Facebook"),
    ("verification.status", "Verification Status"),
    ("phone", "Phone Available"),
    ("indexedAt", "Indexed At"),
)

ENRICHED_COMPANY_FIELDS = (
    ("legalName", "Legal Name"),
    ("domain", "Domain"),
    ("description", "Description"),
    ("foundedYear", "Founded"),
    ("type", "Type"),
    ("ticker", "Ticker"),
    ("tags", "Tags"),
    ("category.sector", "Sector"),
    ("category.industry", "Industry"),
    ("geo.streetAddress", "Street Address"),
    ("geo.city", "City"),
    ("geo.state", "State"),
    ("geo.postalCode", "Postal Code"),
    ("geo.country", "Country"),
    ("metrics.employees", "Employees"),
    ("metrics.annualRevenue", "Annual Revenue"),
    ("metrics.estimatedAnnualRevenue", "Estimated Annual Revenue"),
    ("metrics.raised", "Raised"),
    ("metrics.trafficRank", "Traffic Rank"),
    ("site.phoneNumbers", "Phone Numbers"),
    ("site.emailAddresses", "Email Addresses"),
    ("linkedin.handle", "LinkedIn"),
    ("twitter.handle", "Twitter"),
    ("facebook.handle", "Facebook"),
    ("emailProvider", "Email Provider"),
    ("tech", "Technologies"),
    ("whois.registrar_name", "Registrar"),
    ("whois.created_date", "Domain Created"),
    ("logo", "Logo"),
)


class BaseTombaTransform(DiscoverableTransform):
    """Base class for the Tomba transforms. Not registered as a transform itself."""

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        client = TombaClient.from_settings()
        if client is None:
            response.addUIMessage(CREDENTIALS_MESSAGE, messageType=UIM_FATAL)
            return
        try:
            cls.run(request, response, client)
        except TombaError as e:
            response.addUIMessage(e.message, messageType=e.message_type)

    @classmethod
    def run(cls, request: MaltegoMsg, response: MaltegoTransform, client: TombaClient):
        raise NotImplementedError

    # ---- shared entity builders -------------------------------------------

    @staticmethod
    def inform(response: MaltegoTransform, message: str) -> None:
        response.addUIMessage(message, messageType=UIM_INFORM)

    @staticmethod
    def add_email(response: MaltegoTransform, email_data: Dict[str, Any],
                  email: Optional[str] = None) -> Optional[MaltegoEntity]:
        email = email or email_data.get("email")
        if not email:
            return None
        entity = response.addEntity("maltego.EmailAddress", email)
        add_properties(entity, email_data, EMAIL_FIELDS)
        sources = email_data.get("sources") or []
        if isinstance(sources, list) and sources:
            entity.addProperty("tomba.sources_count", displayName="Sources", value=str(len(sources)))
            uris = [s.get("uri") for s in sources[:3] if isinstance(s, dict) and s.get("uri")]
            if uris:
                entity.addProperty("tomba.source_urls", displayName="Source URLs", value=", ".join(uris))
        return entity

    @staticmethod
    def add_person(response: MaltegoTransform, first_name: Optional[str], last_name: Optional[str],
                   full_name: Optional[str] = None, data: Optional[Dict[str, Any]] = None
                   ) -> Optional[MaltegoEntity]:
        first_name = (first_name or "").strip()
        last_name = (last_name or "").strip()
        full_name = (full_name or f"{first_name} {last_name}").strip()
        if not full_name:
            return None
        entity = response.addEntity("maltego.Person", full_name)
        if first_name:
            entity.addProperty("person.firstnames", displayName="First Names", value=first_name)
        if last_name:
            entity.addProperty("person.lastname", displayName="Surname", value=last_name)
        if data:
            add_properties(entity, data, (
                ("position", "Position"),
                ("department", "Department"),
                ("seniority", "Seniority"),
                ("company", "Company"),
                ("website_url", "Website"),
                ("country", "Country"),
                ("gender", "Gender"),
                ("linkedin", "LinkedIn"),
                ("twitter", "Twitter"),
            ))
        return entity

    @staticmethod
    def add_enriched_person(response: MaltegoTransform, person: Dict[str, Any]) -> Optional[MaltegoEntity]:
        """Person entity from a /people/find or /combined/find person object."""
        name = person.get("name") or {}
        entity = BaseTombaTransform.add_person(
            response, name.get("givenName"), name.get("familyName"), name.get("fullName"))
        if entity is None:
            return None
        add_properties(entity, person, ENRICHED_PERSON_FIELDS)
        return entity

    @staticmethod
    def add_enriched_company(response: MaltegoTransform, company: Dict[str, Any],
                             fallback_name: Optional[str] = None) -> Optional[MaltegoEntity]:
        """Company entity from a /companies/find or /combined/find company object."""
        name = company.get("name") or company.get("legalName") or fallback_name
        if not name:
            return None
        entity = response.addEntity("maltego.Company", name)
        add_properties(entity, company, ENRICHED_COMPANY_FIELDS)
        return entity

    @staticmethod
    def add_phone(response: MaltegoTransform, phone_data: Dict[str, Any],
                  number: Optional[str] = None) -> Optional[MaltegoEntity]:
        number = number or phone_data.get("e164_format") or phone_data.get("intl_format")
        if not number:
            return None
        entity = response.addEntity("maltego.PhoneNumber", number)
        add_properties(entity, phone_data, (
            ("valid", "Valid"),
            ("local_format", "Local Format"),
            ("intl_format", "International Format"),
            ("e164_format", "E.164 Format"),
            ("rfc3966_format", "RFC 3966 Format"),
            ("country_code", "Country Code"),
            ("line_type", "Line Type"),
            ("carrier", "Carrier"),
            ("region.name", "Region"),
            ("region.code", "Region Code"),
            ("timezones", "Time Zones"),
            ("email", "Email"),
            ("domain", "Domain"),
        ))
        return entity
