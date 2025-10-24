#!/usr/bin/env python3
"""
Auto-start script for SuliStreetMeet server and tunnel
Automatically starts the Flask app and creates a tunnel
"""

import subprocess
import time
import sys
import signal
import os
import requests

def check_flask_running():
    """Check if Flask app is running on port 5000"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_flask_app():
    """Start the Flask application"""
    print("Starting Flask application...")
    try:
        # Start Flask app in background
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for Flask to start
        print("Waiting for Flask app to start...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)
            if check_flask_running():
                print("✅ Flask app started successfully!")
                return flask_process
            print(f"Attempt {attempt + 1}/{max_attempts}...")

        print("❌ Flask app failed to start within timeout")
        flask_process.terminate()
        return None

    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return None

def start_tunnel():
    """Start tunnel using setup_tunnel.py with option 2 (LocalTunnel)"""
    print("Starting tunnel with LocalTunnel...")
    try:
        # Start tunnel setup script with option 2 (LocalTunnel)
        tunnel_process = subprocess.Popen(
            [sys.executable, 'setup_tunnel.py', '2'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Read output in real-time to capture the URL
        tunnel_url = None
        while True:
            output = tunnel_process.stdout.readline()
            if output:
                print(output.strip())  # Print the output for user to see
                if 'your url is:' in output.lower():
                    # Extract URL from localtunnel output
                    url = output.split('your url is:')[-1].strip()
                    tunnel_url = url
                    print(f"\n🎉 Tunnel URL: {tunnel_url}")
                    print(f"📱 Access your app at: {tunnel_url}")
                    break
            if tunnel_process.poll() is not None:
                break

        return tunnel_process, tunnel_url

    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None, None

def main():
    print("🚗 SuliStreetMeet Auto Server Starter")
    print("=" * 40)

    flask_process = None
    tunnel_process = None

    try:
        # Check if Flask is already running
        if check_flask_running():
            print("✅ Flask app is already running")
        else:
            # Start Flask app
            flask_process = start_flask_app()
            if not flask_process:
                print("Failed to start Flask app. Exiting.")
                sys.exit(1)

        # Start tunnel
        tunnel_result = start_tunnel()
        if isinstance(tunnel_result, tuple):
            tunnel_process, tunnel_url = tunnel_result
        else:
            tunnel_process = tunnel_result
            tunnel_url = None

        if not tunnel_process:
            print("Failed to start tunnel. Exiting.")
            if flask_process:
                flask_process.terminate()
            sys.exit(1)

        print("\n✅ Server and tunnel are now running!")
        print("📱 Your app should be accessible via the tunnel URL shown above")
        print("Press Ctrl+C to stop everything")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping server and tunnel...")

    finally:
        # Clean up processes
        if tunnel_process:
            print("Stopping tunnel...")
            try:
                tunnel_process.terminate()
                tunnel_process.wait(timeout=5)
            except:
                tunnel_process.kill()

        if flask_process:
            print("Stopping Flask app...")
            try:
                flask_process.terminate()
                flask_process.wait(timeout=5)
            except:
                flask_process.kill()

        print("✅ All processes stopped. Goodbye!")

if __name__ == '__main__':
    main()
