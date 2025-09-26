# Maltego Setup Guide for Tomba.io Transforms

## Quick Setup Steps

1. **Start Transform Server**

   ```bash
   maltego-trx start .
   ```

2. **Add to Maltego**

   - Open Maltego and using Import Config, import the tomba_transforms.mtz file from the repository

3. **Configure API Credentials**
   - In settings.py
   - Add:
     - `TOMBA_API_KEY`: Your API key (starts with 'ta\_')
     - `TOMBA_SECRET_KEY`: Your secret key (starts with 'ts\_')

## Available Transforms

### Core Discovery

- **Domain Search**: Domain → Emails + People + Company

### Email Analysis

- **Email Verifier**: Email → Verified Email
- **Email Enrichment**: Email → Enhanced Data

### Content & Social

- **Author Finder**: URL → Author Email
- **LinkedIn Finder**: LinkedIn URL → Email

### Utility

- **Account Info**: Get API usage stats
- **Phone Finder**: Find phone numbers
- **Phone Validator**: Validate phone numbers
- **Similar Domains**: Find related domains
- **Technology Checker**: Identify tech stack

## Troubleshooting

**"Please configure API credentials"**

- Add API keys in Transform Hub → Server Settings
- Verify keys are correct in Tomba.io dashboard

**"Rate limit exceeded"**

- Wait before making more requests
- Upgrade your Tomba.io plan for higher limits

**"No results found"**

- Try different domains/emails
- Check if data exists publicly
- Verify domain has email addresses
