#!/usr/bin/env python3
"""
Script to start Flask app and test server control functionality
"""

import subprocess
import time
import requests
import sys

def start_flask_app():
    """Start the Flask app in background"""
    print("🚀 Starting Flask app...")
    try:
        process = subprocess.Popen([sys.executable, 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Wait for app to start
        return process
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return None

def test_server_control():
    """Test server control functionality"""
    print("🧪 Testing server control functionality...")

    # Test if Flask app is running
    try:
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"⚠️ Flask app returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return False

    # Test ngrok installation
    try:
        result = subprocess.run(['ngrok', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ngrok is installed")
        else:
            print("❌ ngrok installation issue")
            return False
    except Exception as e:
        print(f"❌ ngrok not found: {e}")
        return False

    print("✅ All basic tests passed!")
    print("\n📋 Manual Testing Instructions:")
    print("1. Open browser to: http://127.0.0.1:5000")
    print("2. Login as admin user")
    print("3. Navigate to: http://127.0.0.1:5000/server_control")
    print("4. Test the 'Make Server Public' button")
    print("5. Verify ngrok tunnel starts and public URL is displayed")
    print("6. Test the 'Make Server Private' button")
    print("7. Verify tunnel stops and server becomes private")

    return True

def main():
    print("🎯 Car Meet App - Server Control Test")
    print("=" * 45)

    # Start Flask app
    flask_process = start_flask_app()
    if not flask_process:
        return

    try:
        # Run tests
        success = test_server_control()

        if success:
            print("\n🎉 Setup complete! Server control functionality is ready.")
            print("Keep this terminal open to keep the Flask app running.")
            print("Press Ctrl+C to stop the server.")
        else:
            print("\n⚠️ Some issues detected. Please check the error messages above.")

        # Keep the script running to maintain Flask app
        try:
            flask_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Flask app...")
            flask_process.terminate()
            flask_process.wait()

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        if flask_process:
            flask_process.terminate()

if __name__ == '__main__':
    main()
