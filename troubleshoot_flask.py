#!/usr/bin/env python3
"""
Flask App Startup Troubleshooter
Diagnoses common Flask app startup issues
"""

import os
import sys
import subprocess
import importlib
import socket

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check")
    print("=" * 25)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("⚠️ Python version might be too old (recommended: 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Dependency Check")
    print("=" * 20)

    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'werkzeug',
        'requests',
        'pyodbc'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed")
        return True

def check_database_files():
    """Check if database files exist"""
    print("\n💾 Database Files Check")
    print("=" * 25)

    db_files = [
        'CarMeetCommunity.accdb',
        'instance/sulistreetmeet.db'
    ]

    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"✅ {db_file} - EXISTS")
        else:
            print(f"❌ {db_file} - MISSING")

    # Check if instance directory exists
    if not os.path.exists('instance'):
        print("❌ instance/ directory - MISSING")
        print("💡 This directory should be created automatically")
    else:
        print("✅ instance/ directory - EXISTS")

def check_port_availability():
    """Check if port 5000 is available"""
    print("\n🔌 Port Availability Check")
    print("=" * 28)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()

    if result == 0:
        print("❌ Port 5000 is already in use")
        print("💡 Another application might be using port 5000")
        print("💡 Try killing the process or use a different port")
        return False
    else:
        print("✅ Port 5000 is available")
        return True

def test_flask_import():
    """Test if Flask app can be imported"""
    print("\n🔧 Flask Import Test")
    print("=" * 20)

    try:
        # Try to import the app
        sys.path.insert(0, os.getcwd())
        import app
        print("✅ Flask app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False

def check_templates():
    """Check if template files exist"""
    print("\n📄 Template Files Check")
    print("=" * 25)

    template_files = [
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html'
    ]

    missing_templates = []
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - MISSING")
            missing_templates.append(template)

    if missing_templates:
        print(f"\n⚠️ Missing templates: {', '.join(missing_templates)}")
        return False
    else:
        print("\n✅ All required templates exist")
        return True

def generate_startup_guide():
    """Generate step-by-step startup guide"""
    print("\n📋 Flask App Startup Guide")
    print("=" * 28)
    print("Follow these steps to start your Flask app:")
    print()
    print("1. 📦 Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. 💾 Check database setup:")
    print("   - Make sure CarMeetCommunity.accdb exists")
    print("   - The instance/ directory should be created automatically")
    print()
    print("3. 🚀 Start the Flask app:")
    print("   python app.py")
    print()
    print("4. 🌐 Verify it's working:")
    print("   - Open browser to: http://127.0.0.1:5000")
    print("   - You should see the Car Meet app homepage")
    print()
    print("5. 🚇 Create public tunnel:")
    print("   python setup_tunnel.py")
    print()
    print("🔧 If you encounter errors:")
    print("   - Check the terminal output for specific error messages")
    print("   - Make sure no other app is using port 5000")
    print("   - Try running: python troubleshoot_flask.py")

def main():
    print("🚗 Car Meet App - Flask Troubleshooter")
    print("=" * 40)

    # Run all checks
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    db_ok = check_database_files()
    port_ok = check_port_availability()
    import_ok = test_flask_import()
    templates_ok = check_templates()

    print("\n📊 Troubleshooting Summary")
    print("=" * 28)
    print(f"Python Version: {'✅' if python_ok else '❌'}")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Database Files: {'✅' if db_ok else '❌'}")
    print(f"Port Available: {'✅' if port_ok else '❌'}")
    print(f"Flask Import: {'✅' if import_ok else '❌'}")
    print(f"Templates: {'✅' if templates_ok else '❌'}")

    # Overall assessment
    all_checks = [python_ok, deps_ok, db_ok, port_ok, import_ok, templates_ok]
    passed_checks = sum(all_checks)

    if passed_checks == len(all_checks):
        print("\n🎉 All checks passed! Your Flask app should start successfully.")
        print("💡 Try running: python app.py")
    else:
        print(f"\n⚠️ {len(all_checks) - passed_checks} issues found that need to be resolved.")
        print("💡 Follow the startup guide below:")

    generate_startup_guide()

if __name__ == '__main__':
    main()
