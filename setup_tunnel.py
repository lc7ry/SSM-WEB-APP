#!/usr/bin/env python3
"""
Setup tunnel script for SuliStreetMeet
Provides multiple options for making the local server publicly accessible
"""

import subprocess
import sys
import time
import os
import requests
import json

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_localtunnel():
    """Check if localtunnel is installed"""
    try:
        result = subprocess.run(['lt', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        # Also check if it's installed globally via npm
        try:
            result = subprocess.run(['npm', 'list', '-g', 'localtunnel'], capture_output=True, text=True)
            return 'localtunnel' in result.stdout
        except:
            return False

def install_ngrok():
    """Install ngrok"""
    print("Installing ngrok...")
    try:
        if sys.platform == "win32":
            # Windows installation
            subprocess.run(['powershell', '-Command',
                          'Invoke-WebRequest -Uri https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip -OutFile ngrok.zip'],
                          check=True)
            subprocess.run(['powershell', '-Command', 'Expand-Archive ngrok.zip -DestinationPath .'], check=True)
            os.rename('ngrok.exe', 'ngrok.exe')  # Just ensure it's there
        else:
            # Linux/Mac installation
            subprocess.run(['curl', '-s', 'https://ngrok-agent.s3.amazonaws.com/ngrok.asc',
                          '|', 'sudo', 'tee', '/etc/apt/trusted.gpg.d/ngrok.asc', '>/dev/null'], check=True)
            subprocess.run(['echo', '"deb https://ngrok-agent.s3.amazonaws.com buster main"',
                          '|', 'sudo', 'tee', '/etc/apt/sources.list.d/ngrok.list'], check=True)
            subprocess.run(['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', 'ngrok'], check=True)
        print("ngrok installed successfully!")
        return True
    except Exception as e:
        print(f"Failed to install ngrok: {e}")
        return False

def install_localtunnel():
    """Install localtunnel"""
    print("Installing localtunnel...")
    try:
        # Try npm first (more reliable for localtunnel)
        try:
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True)
            print("localtunnel installed successfully via npm!")
            return True
        except:
            # Fallback to pip
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'localtunnel-wrapper'], check=True)
            print("localtunnel installed successfully via pip!")
            return True
    except Exception as e:
        print(f"Failed to install localtunnel: {e}")
        print("Please install Node.js from https://nodejs.org/ and try again, or use ngrok instead.")
        return False

def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("Starting ngrok tunnel...")
    print("Make sure your Flask app is running on port 5000!")
    print("If not, open another terminal and run: python app.py")
    print()

    try:
        # Start ngrok
        process = subprocess.Popen(['ngrok', 'http', '5000'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 bufsize=1,
                                 universal_newlines=True)

        # Read output in real-time to capture the URL
        url_found = False
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())  # Print all output
                if 'Forwarding' in output and 'http' in output:
                    # Extract URL from ngrok output like: "Forwarding    https://abc123.ngrok.io -> http://localhost:5000"
                    url_start = output.find('https://')
                    if url_start != -1:
                        url_end = output.find(' ', url_start)
                        if url_end == -1:
                            url = output[url_start:].strip()
                        else:
                            url = output[url_start:url_end].strip()
                        print(f"\n✅ Tunnel started successfully!")
                        print(f"🌐 Public URL: {url}")
                        print(f"📱 Access your app at: {url}")
                        print()
                        print("Press Ctrl+C to stop the tunnel")
                        url_found = True
                        break
            if process.poll() is not None:
                break

        if not url_found:
            print("❌ No tunnel URL found. The tunnel may have failed to start.")
            print("Check ngrok web interface at: http://127.0.0.1:4040")

        process.wait()

    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error starting ngrok tunnel: {e}")

def start_localtunnel():
    """Start localtunnel"""
    print("Starting localtunnel...")
    print("Make sure your Flask app is running on port 5000!")
    print("If not, open another terminal and run: python app.py")
    print()

    try:
        # Start localtunnel
        process = subprocess.Popen(['lt', '--port', '5000'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Read output to get URL
        while True:
            output = process.stdout.readline()
            if output:
                if 'your url is:' in output.lower():
                    url = output.split('your url is:')[-1].strip()
                    print(f"✅ Tunnel started successfully!")
                    print(f"🌐 Public URL: {url}")
                    print(f"📱 Access your app at: {url}")
                    print()
                    print("Press Ctrl+C to stop the tunnel")
                    break
            if process.poll() is not None:
                break

        process.wait()

    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error starting localtunnel: {e}")

def start_serveo_tunnel():
    """Start Serveo SSH tunnel"""
    print("Starting Serveo SSH tunnel...")
    print("Make sure your Flask app is running on port 5000!")
    print("If not, open another terminal and run: python app.py")
    print()

    try:
        # Start Serveo tunnel
        process = subprocess.Popen(['ssh', '-R', '80:localhost:5000', 'serveo.net'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 bufsize=1,
                                 universal_newlines=True)

        # Read output to get URL
        url_found = False
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())  # Print all output
                if 'Forwarding HTTP traffic from' in output:
                    url = output.split('Forwarding HTTP traffic from')[-1].strip()
                    print(f"\n✅ Tunnel started successfully!")
                    print(f"🌐 Public URL: https://{url}")
                    print(f"📱 Access your app at: https://{url}")
                    print()
                    print("Press Ctrl+C to stop the tunnel")
                    url_found = True
                    break
            if process.poll() is not None:
                break

        if not url_found:
            print("❌ No tunnel URL found. The tunnel may have failed to start.")
            print("Check if SSH is available and try again.")

        process.wait()

    except KeyboardInterrupt:
        print("\nStopping tunnel...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error starting Serveo tunnel: {e}")

def main():
    print("SuliStreetMeet Tunnel Setup")
    print("=" * 40)

    # Check command line arguments for auto mode
    if len(sys.argv) > 1:
        try:
            choice = sys.argv[1]
            print(f"Auto-selecting option: {choice}")
        except:
            choice = None
    else:
        # Check if Flask app is running
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

        print("Choose a tunneling option:")
        print("1. ngrok (recommended)")
        print("2. LocalTunnel")
        print("3. Serveo SSH Tunnel")
        print("4. Install ngrok")
        print("5. Install LocalTunnel")
        print("6. Exit")
        print()

        choice = input("Enter your choice (1-6): ").strip()

    if choice == '1':
        if check_ngrok():
            start_ngrok_tunnel()
        else:
            print("❌ ngrok is not installed")
            if input("Install ngrok? (y/n): ").lower() == 'y':
                if install_ngrok():
                    start_ngrok_tunnel()
    elif choice == '2':
        if check_localtunnel():
            start_localtunnel()
        else:
            print("❌ LocalTunnel is not installed")
            if input("Install LocalTunnel? (y/n): ").lower() == 'y':
                if install_localtunnel():
                    start_localtunnel()
    elif choice == '3':
        start_serveo_tunnel()
    elif choice == '4':
        install_ngrok()
    elif choice == '5':
        install_localtunnel()
    elif choice == '6':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
