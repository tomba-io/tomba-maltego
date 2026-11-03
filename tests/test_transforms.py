"""
Offline tests: every transform runs against canned API responses (taken from the
examples in the Tomba OpenAPI spec) with the SDK's HTTP layer patched out.

    python -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ["TOMBA_API_KEY"] = "ta_test"
os.environ["TOMBA_SECRET_KEY"] = "ts_test"

import project  # noqa: E402  registers the transforms
from extensions import registry  # noqa: E402
from maltego_trx.maltego import MaltegoMsg  # noqa: E402
from maltego_trx.server import run_transform  # noqa: E402
from tomba import TombaException  # noqa: E402

EMAIL = {
    "email": "jane.doe@stripe.com", "first_name": "Jane", "last_name": "Doe",
    "full_name": "Jane Doe", "website_url": "stripe.com", "company": "Stripe",
    "position": "Software Engineer", "department": "engineering", "type": "personal",
    "country": "US", "linkedin": "https://www.linkedin.com/in/jane-doe", "score": 100,
    "verification": {"date": "2025-01-15T10:32:00+01:00", "status": "valid"},
    "sources": [{"uri": "https://stripe.com/blog/engineering", "website_url": "stripe.com"}],
}
PHONE = {
    "email": "jane.doe@stripe.com", "domain": "stripe.com", "valid": True,
    "intl_format": "+1 415-555-0132", "e164_format": "+14155550132", "country_code": "US",
    "line_type": "MOBILE", "carrier": "AT&T", "region": {"name": "California", "code": "CA"},
    "timezones": ["America/Los_Angeles"],
}
PERSON = {
    "name": {"fullName": "Jane Doe", "givenName": "Jane", "familyName": "Doe"},
    "email": "jane.doe@stripe.com", "gender": "female",
    "employment": {"domain": "stripe.com", "name": "Stripe", "title": "Software Engineer"},
    "linkedin": {"handle": "https://www.linkedin.com/in/jane-doe"},
}
COMPANY = {
    "name": "Stripe", "legalName": "Stripe", "domain": "stripe.com", "foundedYear": "2010",
    "tags": ["payments", "fintech"], "geo": {"city": "South San Francisco", "country": "United States"},
    "metrics": {"employees": "5K-10K"}, "site": {"phoneNumbers": ["+14155550100"]},
}

RESPONSES = {
    "/domain-search": {"data": {"organization": {"organization": "Stripe", "website_url": "stripe.com",
                                                 "location": {"country": "US"},
                                                 "social_links": {"twitter_url": "https://twitter.com/stripe"}},
                                "emails": [EMAIL]},
                       "meta": {"total": 1, "current": 1, "total_pages": 1}},
    "/email-finder": {"data": EMAIL},
    "/author-finder": {"data": dict(EMAIL, info={"title": "A guide", "publisher_name": "Stripe"})},
    "/linkedin": {"data": EMAIL},
    "/enrich": {"data": EMAIL},
    "/email-format": {"data": [{"format": "{first}.{last}", "percentage": 66},
                               {"format": "{first}", "percentage": 34}]},
    "/location": {"data": [{"name": "US", "total": 450}, {"name": "IE", "total": 120}]},
    "/email-count": {"data": {"total": 1250, "personal_emails": 1100, "generic_emails": 150,
                              "department": {"engineering": 410, "legal": 0},
                              "seniority": {"senior": 420}}},
    "/email-verifier": {"data": {"email": {"email": "jane.doe@stripe.com", "result": "deliverable",
                                           "status": "valid", "score": 99,
                                           "mx": {"records": ["aspmx.l.google.com"]}, "smtp_check": True},
                                 "sources": []}},
    "/email-sources": {"data": [{"uri": "https://stripe.com/blog/engineering", "website_url": "stripe.com",
                                 "still_on_page": True}], "email": "jane.doe@stripe.com"},
    "/people/find": {"data": PERSON},
    "/companies/find": {"data": COMPANY},
    "/combined/find": {"data": {"person": PERSON, "company": COMPANY}},
    "/phone-finder": {"data": PHONE},
    "/phone-validator": {"data": PHONE},
    "/domain-status": {"domain": "gmail.com", "webmail": True, "disposable": False},
    "/domain-suggestions": {"data": [{"name": "Stripe", "domain": "stripe.com", "email_count": 1250}]},
    "/similar": {"data": [{"website_url": "adyen.com", "name": "Adyen", "industries": "financial services"}]},
    "/technology": {"domain": "stripe.com", "data": [
        {"slug": "intercom", "name": "Intercom", "categories": [{"id": 52, "name": "Live chat"}]}]},
    "/reveal/search": {"data": {"companies": [{"name": "Stripe", "website_url": "stripe.com",
                                               "industry": "financial services"}]},
                       "meta": {"total": 1, "page": 1, "pages": 1}},
}

# transform name -> (input value, properties, entity types the output must contain)
CASES = {
    "domainsearch": ("https://www.stripe.com/", "tomba.limit=10", ["maltego.EmailAddress", "maltego.Person", "maltego.Company"]),
    "domainsearchdomain": ("stripe.com", "", ["maltego.EmailAddress", "maltego.Person", "maltego.Company"]),
    "emailfinder": ("Jane Doe", "tomba.domain=stripe.com", ["maltego.EmailAddress"]),
    "authorfinder": ("https://stripe.com/blog/a-guide", "", ["maltego.EmailAddress", "maltego.Person"]),
    "linkedinfinder": ("https://www.linkedin.com/in/jane-doe", "", ["maltego.EmailAddress", "maltego.Person"]),
    "emailenrichment": ("jane.doe@stripe.com", "", ["maltego.EmailAddress", "maltego.Person"]),
    "emailformat": ("stripe.com", "", ["maltego.Phrase"]),
    "location": ("stripe.com", "", ["maltego.Location"]),
    "emailcount": ("stripe.com", "", ["maltego.Phrase"]),
    "emailverifier": ("jane.doe@stripe.com", "", ["maltego.EmailAddress"]),
    "emailsources": ("jane.doe@stripe.com", "", ["maltego.URL"]),
    "personenrichment": ("jane.doe@stripe.com", "", ["maltego.Person"]),
    "companyenrichment": ("stripe.com", "", ["maltego.Company"]),
    "combinedenrichment": ("jane.doe@stripe.com", "", ["maltego.Person", "maltego.Company", "maltego.Domain"]),
    "phonefinder": ("jane.doe@stripe.com", "", ["maltego.PhoneNumber"]),
    "phonefinderdomain": ("stripe.com", "", ["maltego.PhoneNumber"]),
    "phonevalidator": ("+14155550132", "", ["maltego.PhoneNumber"]),
    "domainstatus": ("gmail.com", "", ["maltego.Domain"]),
    "domainsuggestions": ("Stripe", "", ["maltego.Domain"]),
    "similar": ("stripe.com", "", ["maltego.Website"]),
    "technology": ("stripe.com", "", ["maltego.Phrase"]),
    "companiessearch": ("fintech companies in France", "", ["maltego.Company", "maltego.Website"]),
}


def fake_call(responses):
    def call(self, method, path="", headers=None, params=None):
        body = responses[path]
        if isinstance(body, Exception):
            raise body
        return {"data": body, "rate_limit": {}}
    return call


def run(name, value, properties="", responses=RESPONSES):
    args = [value] + ([properties] if properties else [])
    with mock.patch("tomba.client.Client.call", fake_call(responses)):
        output, _status = run_transform(name, MaltegoMsg(LocalArgs=args))
    return output


class TransformTests(unittest.TestCase):
    def test_every_registered_transform_has_a_case(self):
        self.assertEqual(set(registry.transform_metas), set(CASES))
        self.assertNotIn("basetombatransform", registry.transform_metas)

    def test_transforms_produce_expected_entities(self):
        for name, (value, properties, types) in CASES.items():
            with self.subTest(transform=name):
                output = run(name, value, properties)
                self.assertNotIn("FatalError", output, output)
                self.assertNotIn("PartialError", output, output)
                for entity_type in types:
                    self.assertIn(f'Type="{entity_type}"', output, output)

    def test_domain_input_is_normalized(self):
        seen = {}

        def call(self, method, path="", headers=None, params=None):
            seen.update(params or {})
            return {"data": RESPONSES[path], "rate_limit": {}}

        with mock.patch("tomba.client.Client.call", call):
            run_transform("domainsearch", MaltegoMsg(LocalArgs=["https://www.Stripe.com/about"]))
        self.assertEqual(seen["domain"], "stripe.com")
        self.assertEqual(seen["limit"], 10)

    def test_domain_search_person_can_feed_email_finder(self):
        output = run("domainsearch", "stripe.com")
        person = output[output.index('Type="maltego.Person"'):]
        self.assertIn('Name="tomba.website_url">stripe.com<', person)

    def test_api_error_becomes_ui_message(self):
        responses = dict(RESPONSES, **{"/email-verifier": TombaException("Invalid key", 401, {})})
        output = run("emailverifier", "jane.doe@stripe.com", responses=responses)
        self.assertIn("FatalError", output)
        self.assertIn("Invalid Tomba API credentials", output)

    def test_enrichment_not_found_is_informational(self):
        responses = dict(RESPONSES, **{"/people/find": {"errors": {
            "type": "not_found", "message": "The email does not exist in our database", "code": 404}}})
        output = run("personenrichment", "nobody@stripe.com", responses=responses)
        self.assertNotIn("Type=\"maltego.Person\"", output)
        self.assertIn("does not exist", output)

    def test_email_finder_requires_domain(self):
        output = run("emailfinder", "Jane Doe")
        self.assertIn("tomba.domain", output)

    def test_missing_credentials(self):
        with mock.patch.dict(os.environ, {"TOMBA_API_KEY": "", "TOMBA_SECRET_KEY": ""}), \
                mock.patch.dict(sys.modules, {"settings": None}):
            output = run("emailcount", "stripe.com")
        self.assertIn("FatalError", output)
        self.assertIn("credentials are missing", output)


if __name__ == "__main__":
    unittest.main()
