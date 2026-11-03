from maltego_trx.decorator_registry import TransformRegistry

registry = TransformRegistry(
    owner="Tomba technology web service LLC",
    author="Mohamed Ben rebia <b.mohamed@tomba.io>",
    host_url="https://tomba.io",
    seed_ids=["Tomba.Email", "Tomba.Domain", "Tomba.Person"],
)

registry.version = "1.0.0"

DISCLAIMER = (
    "Data from the Tomba API (https://tomba.io). Each run sends one API request "
    "and is charged and rate limited like a direct API call."
)
