# Complete Tomba.io Maltego Integration

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Maltego](https://img.shields.io/badge/Maltego-Compatible-green.svg)](https://maltego.com)
[![Tomba.io](https://img.shields.io/badge/Tomba.io-Official%20SDK-orange.svg)](https://tomba.io)

A comprehensive Maltego integration for Tomba.io using the official Python SDK, providing 11 specialized transforms for email discovery, verification, and enrichment.

## 🚀 Features

### 📧 Core Email Discovery

- **Domain Search**: Find all emails associated with a domain

### 🔍 Email Analysis & Verification

- **Email Verifier**: Verify email deliverability and validity
- **Email Enrichment**: Enrich emails with professional/personal data

### 🌐 Content & Social Intelligence

- **Author Finder**: Extract author emails from article URLs
- **LinkedIn Finder**: Find emails from LinkedIn profiles

### 🛠️ Utility Transforms

- **Account Info**: Check API usage and account status
- **Phone Finder**: Discover phone numbers associated with emails/domains
- **Phone Validator**: Validate phone numbers for correctness
- **Similar Domains**: Find domains related to a given domain
- **Technology Checker**: Identify technologies used by a website

## 📋 Prerequisites

- Python 3.8 or later
- Maltego CE/Classic/XL
- Tomba.io API account ([Sign up here](https://app.tomba.io/auth/register))

## ⚡ Installation

Clone this repo locally.

```bash
git clone https://github.com/tomba-io/tomba-maltego.git
cd tomba-maltego
# Install dependencies
pip install -r requirements.txt
```

**Configure API credentials**:

```bash
cp settings.py.template settings.py
# Edit settings.py with your Tomba.io API keys
```

Open Maltego and using Import Config, import the tomba_transforms.mtz file from the repository

## 🔑 API Configuration

Get your API credentials from [Tomba.io API Dashboard](https://app.tomba.io/api):

```python
# In settings.py
TOMBA_API_KEY = "ta_xxxxxxxxxxxxxxxxxxxx"      # Your API Key
TOMBA_SECRET_KEY = "ts_xxxxxxxxxxxxxxxxxxxx"   # Your Secret Key
```

## 📊 Transform Reference

| Transform          | Input         | Output                  | Description                 |
| ------------------ | ------------- | ----------------------- | --------------------------- |
| Domain Search      | Website       | Emails, People, Company | Find all emails for domain  |
| Email Verifier     | Email         | Verified Email          | Check email deliverability  |
| Email Enrichment   | Email         | Enhanced Email, Person  | Enrich with additional data |
| Author Finder      | URL           | Author Emails, People   | Find article authors        |
| LinkedIn Finder    | LinkedIn URL  | Email, Person           | Find email from profile     |
| Company Enrichment | Domain        | Enhanced Company        | Get company details         |
| Phone Finder       | Email, Domain | Phone Numbers           | Discover associated phones  |
| Phone Validator    | Phone Number  | Validated Phone         | Validate phone number       |
| Similar Domains    | Domain        | Related Domains         | Find similar domains        |
| Technology Checker | Domain        | Technologies            | Identify tech stack         |
| Account Info       | None          | Account Details         | Check API usage             |

## 🎯 Usage Examples

### Basic Domain Search

1. Add Website entity: `example.com`
2. Run **Domain Search [Tomba]**
3. Explore discovered emails and people

### Email Verification

1. Add Email entity: `user@domain.com`
2. Run **Email Verifier [Tomba]**
3. Check verification status and deliverability

## ⚙️ Configuration Options

### Common Issues

**❌ "Please configure API credentials"**

- Add API keys in Transform Hub → Server Settings
- Verify credentials in Tomba.io dashboard

**⚠️ "Rate limit exceeded"**

- Wait before making more requests
- Upgrade Tomba.io plan for higher limits

**📭 "No results found"**

- Try different domains/emails
- Check if data exists publicly
- Verify domain has discoverable emails

### Testing

Run the test suite:

```bash
python test_setup.py              # Test installation

🧪 Testing Setup...
==============================
✅ maltego-trx imported successfully
✅ tomba-io imported successfully
✅ project.py exists
✅ transforms/__init__.py exists
✅ settings.py.template exists
✅ requirements.txt exists

✅ Setup test passed!

📋 Next steps:
1. Copy settings.py.template to settings.py
2. Configure your Tomba.io API credentials
3. Run: ./start_server.sh
4. Add http://localhost:8080 to Maltego

python examples/test_transforms.py # Test API connection
🧪 Tomba.io Transform Test Suite
========================================
🔍 Testing Tomba.io API connection...
✅ API connection successful!
📧 Account: info@tomba.io

🔍 Testing Domain Search...
✅ Found 21 emails for tomba.io
```

## 📈 API Rate Limits

Tomba.io plans and limits:

- **Free**: 25 searches + 50 verifications/month
- **Growth**: 5,000 searches + 10,000 verifications/month
- **Pro**: 20,000 searches + 40,000 verifications/month
- **Enterprise**: 50,000 searches + 100,000 verifications/month

## 🔒 Security & Privacy

- API keys are never logged or exposed
- All requests use HTTPS
- Input validation prevents injection attacks
- Respects rate limits and terms of service
- GDPR and privacy-compliant data handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Tomba.io API Docs](https://docs.tomba.io)
- **Issues**: Create an issue on GitHub
- **API Support**: [Tomba.io Support](https://help.tomba.io)
- **Maltego Help**: [Maltego Documentation](https://docs.maltego.com)

## 🏆 Acknowledgments

- [Tomba.io](https://tomba.io) for the excellent email discovery API
- [Maltego](https://maltego.com) for the Maltego platform
- [maltego-trx](https://github.com/MaltegoTech/maltego-trx) maltego-trx library
