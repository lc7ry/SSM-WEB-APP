#!/usr/bin/env python3
"""
LocalTunnel setup script for SuliStreetMeet
Alternative to ngrok for making local server publicly accessible
"""

import subprocess
import sys
import time
import os

def install_localtunnel():
    """Install localtunnel globally"""
    print("Installing localtunnel...")
    try:
        # Install localtunnel globally
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'localtunnel'], check=True)
        print("✅ LocalTunnel installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to install LocalTunnel: {e}")
        return False

def start_localtunnel():
    """Start localtunnel"""
    print("🚗 Starting LocalTunnel for SuliStreetMeet...")
    print("Make sure your Flask app is running on port 5000!")
    print("If not, open another terminal and run: python app.py")
    print()

    try:
        # Start localtunnel
        print("🌐 Starting tunnel...")
        process = subprocess.Popen(['lt', '--port', '5000'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Read output to get URL
        url_found = False
        while not url_found:
            output = process.stdout.readline()
            if output:
                print(output.strip())  # Print all output for debugging
                if 'your url is:' in output.lower():
                    url = output.split('your url is:')[-1].strip()
                    print()
                    print("✅ Tunnel started successfully!")
                    print(f"🌐 Public URL: {url}")
                    print(f"📱 Access your app at: {url}")
                    print()
                    print("Press Ctrl+C to stop the tunnel")
                    url_found = True
                    break
            if process.poll() is not None:
                break

        if not url_found:
            print("❌ Could not retrieve tunnel URL")
            print("Check the output above for any error messages")

        # Wait for process to finish
        process.wait()

    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error starting LocalTunnel: {e}")

def main():
    print("🚗 SuliStreetMeet LocalTunnel Setup")
    print("=" * 40)

    # Check if Flask app is running
    import requests
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running on port 5000")
        else:
            print("⚠️  Flask app may not be running properly")
    except:
        print("❌ Flask app is not running on port 5000")
        print("Please start it first with: python app.py")
        print()

    print("Choose an option:")
    print("1. Start LocalTunnel")
    print("2. Install LocalTunnel")
    print("3. Exit")
    print()

    choice = input("Enter your choice (1-3): ").strip()

    if choice == '1':
        start_localtunnel()
    elif choice == '2':
        install_localtunnel()
    elif choice == '3':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
