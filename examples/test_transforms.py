#!/usr/bin/env python3
"""
Test script for Tomba.io transforms
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_api_connection():
    """Test API connection"""
    print("🔍 Testing Tomba.io API connection...")

    try:
        from transforms.BaseTombaTransform import TombaSDKWrapper
        from settings import TOMBA_API_KEY, TOMBA_SECRET_KEY

        client = TombaSDKWrapper(TOMBA_API_KEY, TOMBA_SECRET_KEY)
        result = client.get_account_info()
        if "error" in result:
            print(f"❌ API Error: {result['error']}")
            return False
        else:
            print("✅ API connection successful!")
            print(
                f"📧 Account: {result.get('data', {}).get('email', 'Unknown')}")
            return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've configured settings.py")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_domain_search():
    """Test domain search functionality"""
    print("\n🔍 Testing Domain Search...")

    try:
        from transforms.BaseTombaTransform import TombaSDKWrapper
        from settings import TOMBA_API_KEY, TOMBA_SECRET_KEY

        client = TombaSDKWrapper(TOMBA_API_KEY, TOMBA_SECRET_KEY)
        result = client.domain_search("tomba.io", limit=10)

        if "error" in result:
            print(f"❌ Domain search error: {result['error']}")
        else:
            meta = result.get('meta', {})
            print(f"✅ Found {meta.get('total', 0)} emails for tomba.io")

    except Exception as e:
        print(f"❌ Domain search error: {e}")


if __name__ == "__main__":
    print("🧪 Tomba.io Transform Test Suite")
    print("=" * 40)

    # Test API connection
    if test_api_connection():
        test_domain_search()
    else:
        print("\n💡 To fix API issues:")
        print("   1. Copy settings.py.template to settings.py")
        print("   2. Add your Tomba.io API credentials")
        print("   3. Get credentials from: https://app.tomba.io/api")
