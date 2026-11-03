#!/usr/bin/env python3
"""
Quick installation check: dependencies import, the transforms register, and
credentials are found. Makes no API request. Exits non-zero on failure.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def check(label, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {label}{f': {detail}' if detail else ''}")
    return ok


def main():
    print("Tomba Maltego setup check")
    print("=" * 30)
    ok = True

    if sys.version_info < (3, 10):
        ok &= check("Python 3.10+", False, sys.version.split()[0])
    else:
        check("Python 3.10+", True, sys.version.split()[0])

    try:
        import maltego_trx  # noqa: F401
        import tomba  # noqa: F401
        check("maltego-trx and tomba-io import", True)
    except ImportError as e:
        check("maltego-trx and tomba-io import", False, str(e))
        print("\nRun: pip install -r requirements.txt")
        return 1

    try:
        import project  # noqa: F401
        from extensions import registry
        count = len(registry.transform_metas)
        ok &= check("transforms register", count > 0, f"{count} transforms")
    except Exception as e:  # noqa: BLE001
        ok &= check("transforms register", False, repr(e))

    from transforms.base import get_credentials
    api_key, secret = get_credentials()
    if api_key and secret:
        check("credentials found", True)
    else:
        print("note credentials not set yet: copy settings.py.template to settings.py "
              "or export TOMBA_API_KEY and TOMBA_SECRET_KEY")

    if not ok:
        print("\nSetup check failed.")
        return 1

    print("\nSetup check passed. Next steps:")
    print("1. Download tomba_transforms.mtz from https://github.com/tomba-io/tomba-maltego/releases/latest")
    print("2. In Maltego: Import | Export > Import Config > tomba_transforms.mtz")
    print(f"3. In the Transform Manager, set each Tomba transform's working directory to {ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
