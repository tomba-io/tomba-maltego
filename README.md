# [<img src="https://tomba.io/logo.svg" alt="Tomba" width="25"/>](https://tomba.io/) Tomba Maltego Transforms

> The #1 Rated Email Intelligence Platform — Find professional emails with unmatched accuracy, right inside your Maltego graphs.

[![Latest Release](https://img.shields.io/github/v/release/tomba-io/tomba-maltego)](https://github.com/tomba-io/tomba-maltego/releases/latest)
[![Build and release](https://github.com/tomba-io/tomba-maltego/actions/workflows/release.yml/badge.svg)](https://github.com/tomba-io/tomba-maltego/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/github/license/tomba-io/tomba-maltego)](LICENSE)

22 local Maltego transforms for the [Tomba API](https://docs.tomba.io), built on the official [`tomba-io`](https://pypi.org/project/tomba-io/) Python SDK and [`maltego-trx`](https://github.com/MaltegoTech/maltego-trx). They cover every Tomba lookup: domain search, email finder, verifier, enrichment, phone finder and validator, company search, technologies and similar companies.

## About Tomba

[Tomba.io](https://tomba.io) is the #1 rated email intelligence platform, trusted by **150,000+ sales teams** worldwide.

- **Best Email Finder** — 98% accuracy, ranked #1 in independent benchmarks
- **Best Email Verification** — Real-time SMTP verification with catch-all detection
- **Best Phone Finder** — Direct dial numbers linked to professional emails
- **Best Domain Search** — 450M+ verified contacts across all industries
- **81% Coverage** — The highest in the industry, proven in 5,000-lead independent tests

### Why Tomba?

| Feature             | Tomba              | Others        |
| ------------------- | ------------------ | ------------- |
| Email Coverage      | **81%**            | 30-60%        |
| Verification        | **Real-time SMTP** | Pattern-based |
| Phone Numbers       | **Direct dials**   | Limited       |
| Catch-all Detection | **AI-powered**     | Basic         |
| API Rate Limits     | **Generous**       | Restrictive   |

[Get your free API key](https://app.tomba.io/auth/register) — No credit card required.

## Getting Started

1. **Sign up** for a free account at [app.tomba.io](https://app.tomba.io/auth/register)
2. **Get your API key and secret** from the [API dashboard](https://app.tomba.io/api)
3. **Install** the transforms and import them into Maltego (see below)
4. **Run a transform** on a Website, Domain, Email Address, Person or Phone Number entity

## Installation

**Requirements:** Python 3.10 or later (required by `maltego-trx`), and Maltego Desktop.

The transforms run as local transforms: for each run, Maltego starts `python3 project.py local <transform>` in a clone of this repository.

1. Clone the repository and install the dependencies:

    ```bash
    git clone https://github.com/tomba-io/tomba-maltego.git
    cd tomba-maltego
    pip install -r requirements.txt
    ```

2. Download `tomba_transforms.mtz` from the [latest release](https://github.com/tomba-io/tomba-maltego/releases/latest).
3. In Maltego, go to **Import | Export > Import Config** and select `tomba_transforms.mtz`. The transforms appear under **Local** in the Transform Manager, with names starting with **Tomba -**.
4. The imported transforms run `python3` from the placeholder directory `/path/to/tomba-maltego`. In **Transforms > Transform Manager**, set each Tomba transform's **Working directory** to your clone. If you installed the dependencies in a virtual environment, also set **Command line** to that environment's Python, for example `/home/you/tomba-maltego/.venv/bin/python`.

## Authentication

The transforms look for your key and secret in two places, in this order:

1. The `TOMBA_API_KEY` and `TOMBA_SECRET_KEY` environment variables.
2. A `settings.py` file next to `project.py`.

Maltego Desktop usually doesn't pass your shell's environment to local transforms, so use `settings.py` with Maltego:

```bash
cp settings.py.template settings.py
```

```python
# settings.py (gitignored)
TOMBA_API_KEY = "ta_xxxxxxxxxxxxxxxxxxxx"      # Your API key (starts with 'ta_')
TOMBA_SECRET_KEY = "ts_xxxxxxxxxxxxxxxxxxxx"   # Your secret (starts with 'ts_')
```

Environment variables suit the command line, CI and the transform server:

```bash
export TOMBA_API_KEY="ta_xxxx"
export TOMBA_SECRET_KEY="ts_xxxx"
```

## Quick Start

Map the people at a company:

1. Add a **Website** entity with the value `stripe.com`.
2. Run **Tomba - Domain Search**. Maltego adds an Email Address entity for each address, a Person entity for each named person, and a Company entity.
3. Select the Email Address entities and run **Tomba - Email Verifier**.
4. Select a Person and run **Tomba - Email Finder**. The person already carries the company website from step 2.

Every transform can also be run from a terminal, which is handy for checking credentials:

```bash
python3 project.py local domainsearch stripe.com "tomba.limit=10"
```

Each run sends one API request, so it's charged and rate limited like a direct API call. See [Credit costs](https://docs.tomba.io/usage-and-quotas#credit-costs) and [Rate limits](https://docs.tomba.io/rate-limits).

## Transforms

| Transform | Input | Output | Endpoint |
| --- | --- | --- | --- |
| Tomba - Domain Search | Website | Email Address, Person, Company | [`GET /domain-search`](https://docs.tomba.io/api/finder#domain-search) |
| Tomba - Domain Search (Domain) | Domain | Email Address, Person, Company | [`GET /domain-search`](https://docs.tomba.io/api/finder#domain-search) |
| Tomba - Email Finder | Person | Email Address | [`GET /email-finder`](https://docs.tomba.io/api/finder#email-finder) |
| Tomba - Email Verifier | Email Address | Email Address | [`GET /email-verifier`](https://docs.tomba.io/api/verifier#email-verifier) |
| Tomba - Email Enrichment | Email Address | Email Address, Person | [`GET /enrich`](https://docs.tomba.io/api/finder#email-enrichment) |
| Tomba - Author Finder | URL | Email Address, Person | [`GET /author-finder`](https://docs.tomba.io/api/finder#author-finder) |
| Tomba - LinkedIn Finder | URL | Email Address, Person | [`GET /linkedin`](https://docs.tomba.io/api/finder#linkedin-finder) |
| Tomba - Email Count | Domain | Phrase | [`GET /email-count`](https://docs.tomba.io/api/finder#email-count) |
| Tomba - Email Format | Domain | Phrase | [`GET /email-format`](https://docs.tomba.io/api/finder#email-format) |
| Tomba - Location | Domain | Location | [`GET /location`](https://docs.tomba.io/api/finder#location) |
| Tomba - Email Sources | Email Address | URL | [`GET /email-sources`](https://docs.tomba.io/api/email#email-sources) |
| Tomba - Person Enrichment | Email Address | Person | [`GET /people/find`](https://docs.tomba.io/api/enrichment#person-api) |
| Tomba - Company Enrichment | Domain | Company | [`GET /companies/find`](https://docs.tomba.io/api/enrichment#company-api) |
| Tomba - Combined Enrichment | Email Address | Person, Company, Domain | [`GET /combined/find`](https://docs.tomba.io/api/enrichment#combined-api) |
| Tomba - Phone Finder | Email Address | Phone Number | [`GET /phone-finder`](https://docs.tomba.io/api/phone#phone-finder) |
| Tomba - Phone Finder (Domain) | Domain | Phone Number | [`GET /phone-finder`](https://docs.tomba.io/api/phone#phone-finder) |
| Tomba - Phone Validator | Phone Number | Phone Number | [`GET /phone-validator`](https://docs.tomba.io/api/phone#phone-validator) |
| Tomba - Domain Status | Domain | Domain | [`GET /domain-status`](https://docs.tomba.io/api/domain#domain-status) |
| Tomba - Domain Suggestions | Company | Domain | [`GET /domain-suggestions`](https://docs.tomba.io/api/domain-suggestions#get-domain-suggestions) |
| Tomba - Similar Websites | Website | Website | [`GET /similar`](https://docs.tomba.io/api/domain#similar) |
| Tomba - Technology | Domain | Phrase | [`GET /technology`](https://docs.tomba.io/api/domain#technology) |
| Tomba - Companies Search | Phrase | Company, Website | [`POST /reveal/search`](https://docs.tomba.io/api/reveal#search-companies) |

Some transforms read optional **entity properties**. Add them to the input entity in Maltego's Property View before you run the transform. From the command line, pass them as the third argument, `name=value` pairs separated by `#`.

### Domain Search

Find the email addresses, people and company behind a website. **Domain Search (Domain)** does the same on a Domain entity.

| Property | Default | Meaning |
| --- | --- | --- |
| `tomba.limit` | `10` | Addresses per request, one of the [allowed values](https://docs.tomba.io/api/finder#domain-search) (`10`, `20`, `50`, `100`, …). Each 10 requested, rounded up, costs one search credit. On the Free plan a limit above 10 fails. |
| `tomba.page` | `1` | Result page |
| `tomba.department` | | Only these departments, comma-separated, such as `engineering,sales` |
| `tomba.country` | | Only people in this country, as a two-letter code such as `US` |
| `tomba.min_score` | `0` | Drop addresses with a lower confidence score |

```bash
python3 project.py local domainsearch stripe.com "tomba.limit=20#tomba.department=engineering"
python3 project.py local domainsearchdomain stripe.com
```

### Email Finder

Find a person's email address from their name and company domain. The domain comes from the Person's `tomba.domain` property, or from `tomba.website_url`, which Domain Search, Email Enrichment and the other finders set. The name comes from `person.firstnames` and `person.lastname`, or from the entity value.

```bash
python3 project.py local emailfinder "Jane Doe" "tomba.domain=stripe.com"
```

### Email Verifier

Verify an email address: status, result, score, SMTP and MX checks, accept-all, disposable and webmail flags.

```bash
python3 project.py local emailverifier jane.doe@stripe.com
```

### Email Enrichment

Enrich an email address with the person's name, position, company and social profiles.

```bash
python3 project.py local emailenrichment jane.doe@stripe.com
```

### Author Finder

Find the email address of the author of an article URL.

```bash
python3 project.py local authorfinder https://stripe.com/blog/online-payments-guide
```

### LinkedIn Finder

Find the email address of the person behind a LinkedIn profile URL.

```bash
python3 project.py local linkedinfinder https://www.linkedin.com/in/jane-doe
```

### Email Count

Count the addresses Tomba has for a domain, with properties for personal, generic, each department and each seniority level.

```bash
python3 project.py local emailcount stripe.com
```

### Email Format

List the address patterns a domain uses, such as `{first}.{last}@stripe.com`, each with its share.

```bash
python3 project.py local emailformat stripe.com
```

### Location

Break down a domain's addresses by country, one Location entity per country.

```bash
python3 project.py local location stripe.com
```

### Email Sources

List the web pages where Tomba found an email address, with when each was first and last seen.

```bash
python3 project.py local emailsources jane.doe@stripe.com
```

### Person Enrichment

Get a person's profile from their email address: name, location, employment, and LinkedIn, Twitter, GitHub and Facebook handles.

```bash
python3 project.py local personenrichment jane.doe@stripe.com
```

### Company Enrichment

Get a company's profile from its domain: industry, size, revenue, address, technologies, WHOIS and social handles.

```bash
python3 project.py local companyenrichment stripe.com
```

### Combined Enrichment

Get the person and their company from one email address.

```bash
python3 project.py local combinedenrichment jane.doe@stripe.com
```

### Phone Finder

Find the phone number linked to an email address. **Phone Finder (Domain)** finds a domain's phone number.

```bash
python3 project.py local phonefinder jane.doe@stripe.com
python3 project.py local phonefinderdomain stripe.com
```

### Phone Validator

Validate a phone number in international format and get its formats, line type, carrier, region and time zones.

```bash
python3 project.py local phonevalidator +14155550132
```

### Domain Status

Check whether a domain belongs to a webmail or disposable email provider.

```bash
python3 project.py local domainstatus gmail.com
```

### Domain Suggestions

Find the domains of up to five companies whose name matches a Company entity.

```bash
python3 project.py local domainsuggestions Stripe
```

### Similar Websites

Find the websites of companies similar to a website.

```bash
python3 project.py local similar stripe.com
```

### Technology

List the technologies a domain's website uses, one Phrase entity per technology with its categories. Domains that share a technology end up linked to the same entity.

```bash
python3 project.py local technology stripe.com
```

### Companies Search

Search Tomba's company database with a natural-language query on a Phrase entity, such as `fintech companies in France`. It returns up to 50 companies per page. Set `tomba.page` for later pages.

```bash
python3 project.py local companiessearch "fintech companies in France"
```

## Building & Releasing

`project.py build` writes `tomba_transforms.mtz`, plus the `transforms.csv` and `settings.csv` configs for a Maltego iTDS:

```bash
python3 project.py build [--mtz PATH] [--working-dir DIR] [--python CMD] [--version X] [--no-debug] [--no-csv]
```

| Option | Default |
| --- | --- |
| `--mtz` | `tomba_transforms.mtz` in the project |
| `--working-dir` | This project's absolute path |
| `--python` | The Python running the build |
| `--version` | `registry.version` in `extensions.py` |
| `--no-debug` | Off: transform output is shown in Maltego's output window |

The `.mtz` is a build artifact and isn't committed. The [Build and release](.github/workflows/release.yml) workflow runs the setup check, the offline tests and the build on every push and pull request, with Python 3.10 and 3.12. To publish a release, push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow then builds `tomba_transforms.mtz`, with the placeholder working directory and the tag as its version, and attaches it and `transforms.csv` to a new GitHub Release.

To serve the transforms over HTTP instead (iTDS or TDS), run `./start_server.sh` or `docker compose up`. Both listen on port 8080.

## Testing

```bash
python3 test_setup.py                     # dependencies, transform registration, credentials
python3 -m unittest discover -s tests -v  # every transform against canned API responses, offline
python3 examples/test_transforms.py       # live check with your key: a free domain status check and one domain search
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| "Tomba API credentials are missing" | Create `settings.py` from the template and set both values. Maltego doesn't see shell environment variables. |
| The transform fails to start, or Maltego reports an exit code | In the Transform Manager, check that the transform's working directory points to your clone, and that its command line is a Python that has `maltego-trx` and `tomba-io` installed. |
| "Invalid Tomba API credentials" | Check the key and secret on the [API dashboard](https://app.tomba.io/api). |
| "Not enough Tomba credits" or "rate limit reached" | See [Usage and quotas](https://docs.tomba.io/usage-and-quotas) and [Rate limits](https://docs.tomba.io/rate-limits). |
| Any other Tomba error | Look it up in [Errors](https://docs.tomba.io/error-handling#error-types). |

## Documentation

See the [Maltego integration guide](https://docs.tomba.io/integrations/maltego) and the [official documentation](https://docs.tomba.io/).

## About Tomba

Founded to solve the problem of unreliable email data, [Tomba.io](https://tomba.io) is the leading B2B email intelligence platform. Our AI-powered engine searches, verifies, and enriches professional contact data with unmatched accuracy.

### Products

- **[Email Finder](https://tomba.io/email-finder)** — Find any professional email address
- **[Email Verifier](https://tomba.io/email-verifier)** — Verify emails in real-time
- **[Domain Search](https://tomba.io/domain-search)** — Find all emails for a company
- **[Phone Finder](https://tomba.io/phone-finder)** — Find direct phone numbers
- **[Bulk Enrichment](https://tomba.io/bulks)** — Enrich contacts at scale
- **[AI Company Search](https://tomba.io/reveal)** — Find companies with AI-powered search
- **[CLI](https://tomba.io/cli)** — Command-line interface for Tomba
- **[MCP Server](https://tomba.io/mcp)** — Connect AI tools (Claude, ChatGPT, Cursor) to Tomba
- **[REST API](https://tomba.io/api)** — Full programmatic access

### Browser Extensions & Add-ons

- **[Chrome Extension](https://chromewebstore.google.com/detail/tomba-email-finder-email/icmjegjggphchjckknoooajmklibccjb)** — Find emails while browsing
- **[Google Sheets Add-on](https://tomba.io/sheets)** — Enrich leads in spreadsheets
- **[Microsoft Excel Add-in](https://tomba.io/excel)** — Email finder in Excel
- **[Airtable Integration](https://tomba.io/airtable)** — Connect with Airtable

### Integrations

50+ CRM and sales tool integrations:
[Salesforce](https://tomba.io/integrations) · [HubSpot](https://tomba.io/integrations) · [Zapier](https://tomba.io/integrations) · [Pipedrive](https://tomba.io/integrations) · [and more...](https://tomba.io/integrations)

### Tomba SDKs

| Language | Package                                                     |
| -------- | ----------------------------------------------------------- |
| Node.js  | [tomba](https://www.npmjs.com/package/tomba)                |
| Python   | [tomba-io](https://pypi.org/project/tomba-io/)              |
| PHP      | [tomba-io/php](https://packagist.org/packages/tomba-io/php) |
| Ruby     | [tomba](https://rubygems.org/gems/tomba)                    |
| Go       | [tomba-io/go](https://pkg.go.dev/github.com/tomba-io/go)    |
| Rust     | [tomba](https://crates.io/crates/tomba)                     |
| Dart     | [tomba](https://pub.dev/packages/tomba)                     |
| Deno     | [@tomba/sdk](https://jsr.io/@tomba/sdk)                     |
| Elixir   | [tomba](https://hex.pm/packages/tomba)                      |
| C#       | [Tomba](https://www.nuget.org/packages/Tomba)               |
| Perl     | [Tomba::Client](https://metacpan.org/pod/Tomba::Client)     |
| Lua      | [tomba](https://luarocks.org/modules/tomba/tomba)           |
| R        | [tomba](https://github.com/tomba-io/r)                      |

### Resources

- [Blog](https://tomba.io/blog)
- [Help Center](https://help.tomba.io)
- [API Documentation](https://docs.tomba.io)
- [Pricing](https://tomba.io/pricing)
- [Status Page](https://status.tomba.io)

---

**[Try Tomba Free](https://app.tomba.io/auth/register)** — Find your first email in seconds. No credit card required.

## License

Licensed under the [MIT License](LICENSE).
