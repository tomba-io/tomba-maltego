#!/usr/bin/env python3
"""
Quick setup test
"""


def test_imports():
    """Test that all imports work"""
    try:
        import maltego_trx
        print("✅ maltego-trx imported successfully")

        import tomba
        print("✅ tomba-io imported successfully")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_project_structure():
    """Test project structure"""
    import os

    required_files = [
        'project.py',
        'transforms/__init__.py',
        'settings.py.template',
        'requirements.txt'
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False

    return True


if __name__ == "__main__":
    print("🧪 Testing Setup...")
    print("=" * 30)

    imports_ok = test_imports()
    structure_ok = test_project_structure()

    if imports_ok and structure_ok:
        print("\n✅ Setup test passed!")
        print("\n📋 Next steps:")
        print("1. Copy settings.py.template to settings.py")
        print("2. Configure your Tomba.io API credentials")
        print("3. Run: ./start_server.sh")
        print("4. Add http://localhost:8080 to Maltego")
    else:
        print("\n❌ Setup test failed!")
        print("Please check the errors above.")
