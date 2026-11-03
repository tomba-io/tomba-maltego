#!/usr/bin/env python3
"""
Live check against the Tomba API with your credentials (settings.py or the
TOMBA_API_KEY / TOMBA_SECRET_KEY environment variables).

The domain status check is free; the domain search costs one search credit.

    python3 examples/test_transforms.py [domain]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transforms.base import TombaClient, TombaError  # noqa: E402


def main():
    domain = sys.argv[1] if len(sys.argv) > 1 else "tomba.io"
    client = TombaClient.from_settings()
    if client is None:
        print("Credentials not found. Copy settings.py.template to settings.py, or export "
              "TOMBA_API_KEY and TOMBA_SECRET_KEY. Get them at https://app.tomba.io/api")
        return 1

    try:
        status = client.domain_status("gmail.com")
        print(f"ok   API connection: gmail.com webmail={status.get('webmail')}")

        body = client.domain_search(domain, limit=10)
        emails = (body.get("data") or {}).get("emails") or []
        total = (body.get("meta") or {}).get("total", len(emails))
        print(f"ok   Domain Search: {len(emails)} addresses returned for {domain} ({total} in total)")
    except TombaError as e:
        print(f"FAIL {e.message}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
