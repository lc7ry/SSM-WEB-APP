#!/usr/bin/env python3
"""
Comprehensive tunnel diagnostic script
Tests Flask app, ngrok, and provides detailed troubleshooting
"""

import os
import subprocess
import sys
import time
import requests
import socket
from pathlib import Path

def check_flask_app_detailed():
    """Detailed Flask app check"""
    print("🔍 Detailed Flask App Check")
    print("=" * 30)

    # Check if port 5000 is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()

    if result == 0:
        print("✅ Port 5000 is open")
    else:
        print("❌ Port 5000 is closed")
        return False

    # Test HTTP request
    try:
        response = requests.get('http://127.0.0.1:5000', timeout=10)
        print(f"✅ HTTP Response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Flask app is responding correctly")
            return True
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Flask app not responding")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
        return False

def test_ngrok_directly():
    """Test ngrok directly"""
    print("\n🔧 Testing ngrok directly")
    print("=" * 25)

    try:
        # Test ngrok version
        result = subprocess.run(['ngrok', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ ngrok version: {result.stdout.strip()}")
        else:
            print(f"❌ ngrok version check failed: {result.stderr}")
            return False

        # Test ngrok help
        result = subprocess.run(['ngrok', '--help'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ngrok help command works")
        else:
            print(f"❌ ngrok help failed: {result.stderr}")
            return False

        return True
    except FileNotFoundError:
        print("❌ ngrok.exe not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error testing ngrok: {e}")
        return False

def test_ngrok_tunnel():
    """Test creating ngrok tunnel"""
    print("\n🚀 Testing ngrok tunnel creation")
    print("=" * 32)

    try:
        # Start ngrok tunnel
        print("Starting ngrok tunnel on port 5000...")
        process = subprocess.Popen(['ngrok', 'http', '5000'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

        # Wait for ngrok to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print("✅ ngrok process started successfully")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ ngrok process failed to start")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False

        # Try to get tunnel info
        try:
            response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'https':
                            public_url = tunnel.get('public_url')
                            print(f"✅ Tunnel created: {public_url}")
                            process.terminate()
                            return True
                else:
                    print("⚠️ No tunnels found yet, but ngrok is running")
                    process.terminate()
                    return True
            else:
                print(f"⚠️ ngrok API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not connect to ngrok API: {e}")

        # If we get here, terminate the process
        process.terminate()
        return False

    except Exception as e:
        print(f"❌ Error testing tunnel: {e}")
        return False

def check_network_connectivity():
    """Check network connectivity"""
    print("\n🌐 Network Connectivity Check")
    print("=" * 30)

    try:
        # Test internet connectivity
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            print("✅ Internet connectivity: OK")
        else:
            print(f"⚠️ Internet connectivity: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Internet connectivity: Failed ({e})")
        return False

    try:
        # Test ngrok connectivity
        response = requests.get('https://ngrok.com', timeout=5)
        if response.status_code == 200:
            print("✅ ngrok website: Accessible")
        else:
            print(f"⚠️ ngrok website: Status {response.status_code}")
    except Exception as e:
        print(f"⚠️ ngrok website: Not accessible ({e})")

    return True

def main():
    print("🚗 Car Meet App - Tunnel Diagnostic Tool")
    print("=" * 45)

    # Run all checks
    flask_ok = check_flask_app_detailed()
    ngrok_ok = test_ngrok_directly()
    network_ok = check_network_connectivity()

    print("\n📊 Diagnostic Summary")
    print("=" * 20)
    print(f"Flask App: {'✅ OK' if flask_ok else '❌ FAILED'}")
    print(f"ngrok: {'✅ OK' if ngrok_ok else '❌ FAILED'}")
    print(f"Network: {'✅ OK' if network_ok else '❌ FAILED'}")

    if flask_ok and ngrok_ok:
        print("\n🎯 Testing tunnel creation...")
        tunnel_ok = test_ngrok_tunnel()
        if tunnel_ok:
            print("\n🎉 All systems ready! You can now run:")
            print("   python setup_tunnel.py")
        else:
            print("\n❌ Tunnel creation failed")
            print("💡 Try running the tunnel setup anyway - it might work")
    else:
        print("\n❌ Prerequisites not met")
        if not flask_ok:
            print("💡 Start your Flask app first: python app.py")
        if not ngrok_ok:
            print("💡 Check if ngrok.exe is in the current directory")

    print("\n🔧 Troubleshooting Tips:")
    print("1. Make sure Flask app is running: python app.py")
    print("2. Check if ngrok.exe exists in current directory")
    print("3. Try running: python setup_tunnel.py")
    print("4. If still failing, check firewall/antivirus settings")

if __name__ == '__main__':
    main()
