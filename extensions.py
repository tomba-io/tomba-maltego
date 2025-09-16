from maltego_trx.decorator_registry import TransformRegistry
# from settings import api_key_setting, secret_key_setting

registry = TransformRegistry(
    owner="Tomba technology web service LLC",
    author="Mohamed Ben rebia <b.mohamed@tomba.io>",
    host_url="https://tomba.io",
    seed_ids=["Tomba.Email", "Tomba.Domain", "Tomba.Person"],
)

registry.version = "0.1"

# registry.global_settings = [api_key_setting, secret_key_setting]
