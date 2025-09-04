#!/usr/bin/env python3
"""
Multiple Tunneling Alternatives - When Serveo/ngrok are blocked
This script provides several working alternatives for making your Flask app public.
"""

import subprocess
import sys
import os
import time
import requests
from threading import Thread

def check_flask_running():
    """Check if Flask app is running on port 5000"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        return response.status_code == 200
    except:
        return False

def try_localtunnel():
    """Try LocalTunnel (requires Node.js)"""
    print("🌐 Trying LocalTunnel...")
    try:
        # Check if Node.js is installed
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Node.js not found. Download from https://nodejs.org/")
            return False

        # Check if localtunnel is installed
        result = subprocess.run(['lt', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("📦 Installing LocalTunnel...")
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True, timeout=60)

        print("✅ LocalTunnel ready!")
        print("🚀 Starting tunnel...")
        print("📝 Your public URL will appear below:")
        print("💡 Press Ctrl+C to stop\n")

        # Start the tunnel
        subprocess.run(['lt', '--port', '5000'], check=True)

    except subprocess.TimeoutExpired:
        print("⏰ LocalTunnel installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ LocalTunnel error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 LocalTunnel stopped")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True

def try_pagekite():
    """Try PageKite (Python-based tunneling)"""
    print("🌐 Trying PageKite...")
    try:
        # Install pagekite if not available
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pagekite'], check=True, timeout=60)

        print("✅ PageKite installed!")
        print("🚀 Starting tunnel...")
        print("📝 Your public URL will be: https://yourname.pagekite.me")
        print("💡 Press Ctrl+C to stop\n")

        # Note: PageKite requires a free account for custom domains
        print("⚠️  PageKite requires a free account. Visit: https://pagekite.net/")
        print("   For testing, use a temporary subdomain\n")

        # This would require user interaction, so we'll provide instructions instead
        print("📖 Manual PageKite setup:")
        print("1. Sign up at https://pagekite.net/")
        print("2. Run: pagekite.py 5000 yourname.pagekite.me")
        print("3. Share: https://yourname.pagekite.me\n")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ PageKite installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PageKite error: {e}")
        return False

def try_cloudflared():
    """Try Cloudflare Tunnel (cloudflared)"""
    print("🌐 Trying Cloudflare Tunnel...")
    try:
        # Check if cloudflared is installed
        result = subprocess.run(['cloudflared', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("📦 Installing Cloudflare Tunnel...")
            # Download and install cloudflared
            if os.name == 'nt':  # Windows
                subprocess.run(['powershell', '-Command',
                    'Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"'],
                    check=True, timeout=60)
            else:  # Linux/Mac
                subprocess.run(['curl', '-L', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64',
                    '-o', 'cloudflared'], check=True, timeout=60)
                os.chmod('cloudflared', 0o755)

        print("✅ Cloudflare Tunnel ready!")
        print("🚀 Starting tunnel...")
        print("📝 Your public URL will appear below:")
        print("💡 Press Ctrl+C to stop\n")

        # Start the tunnel
        subprocess.run(['cloudflared', 'tunnel', '--url', 'http://localhost:5000'], check=True)

    except subprocess.TimeoutExpired:
        print("⏰ Cloudflare Tunnel installation timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Cloudflare Tunnel error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Cloudflare Tunnel stopped")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    return True

def show_manual_options():
    """Show manual tunneling options"""
    print("\n📖 Manual Tunneling Options:")
    print("=" * 40)

    print("1. 🌐 Ngrok (if IP not blocked):")
    print("   - Download: https://ngrok.com/download")
    print("   - Run: ngrok http 5000")
    print("   - Use different network/VPN if blocked")

    print("\n2. 🔗 LocalTunnel (Node.js required):")
    print("   - Install Node.js: https://nodejs.org/")
    print("   - Run: npm install -g localtunnel")
    print("   - Run: lt --port 5000")

    print("\n3. 📡 Serveo Alternatives:")
    print("   - Try different SSH service")
    print("   - Use: ssh -R 80:localhost:5000 ssh.localhost.run")
    print("   - Or: ssh -R 80:localhost:5000 nokey@localhost.run")

    print("\n4. ☁️  Cloudflare Tunnel:")
    print("   - Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/")
    print("   - Run: cloudflared tunnel --url http://localhost:5000")

    print("\n5. 📧 PageKite:")
    print("   - Sign up: https://pagekite.net/")
    print("   - Run: pagekite.py 5000 yourname.pagekite.me")

    print("\n6. 🏠 Port Forwarding:")
    print("   - Configure your router to forward port 5000")
    print("   - Find your public IP: https://whatismyipaddress.com/")
    print("   - Share: http://YOUR_PUBLIC_IP:5000")

def main():
    print("🚀 SuliStreetMeet Public Access Setup")
    print("=" * 40)

    # Check if Flask is running
    if not check_flask_running():
        print("❌ Flask app not detected on port 5000")
        print("💡 Start your Flask app first: python app.py")
        print("   Then run this script again\n")
        return

    print("✅ Flask app detected on port 5000")

    # Try different tunneling options
    options = [
        ("LocalTunnel", try_localtunnel),
        ("Cloudflare Tunnel", try_cloudflared),
        ("PageKite", try_pagekite),
    ]

    success = False
    for name, func in options:
        try:
            if func():
                success = True
                break
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            continue

    if not success:
        print("❌ All automatic options failed")
        show_manual_options()

    print("\n💡 Tips:")
    print("- Try different networks or VPN if services are blocked")
    print("- Some services may require free accounts")
    print("- For production, consider Heroku, Railway, or Vercel")

if __name__ == "__main__":
    main()
