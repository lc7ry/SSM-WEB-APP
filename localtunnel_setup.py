#!/usr/bin/env python3
"""
LocalTunnel Setup Script - Alternative to ngrok
This script provides a simple way to make your Flask app public using LocalTunnel.
"""

import subprocess
import sys
import os

def setup_localtunnel():
    """Install and run LocalTunnel as an alternative to ngrok"""
    print("🚀 Setting up LocalTunnel as an alternative to ngrok...")

    try:
        # Check if Node.js is installed
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js is not installed.")
            print("📥 Please download and install Node.js from: https://nodejs.org/")
            print("   Choose the LTS version for stability")
            return False

        print("✅ Node.js found:", result.stdout.strip())

        # Check if npm is available
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ npm is not available. It should come with Node.js.")
            return False

        print("✅ npm found:", result.stdout.strip())

        # Install LocalTunnel globally using npm
        print("📦 Installing LocalTunnel...")
        subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True)

        print("✅ LocalTunnel installed successfully!")
        print("\n📋 To use LocalTunnel:")
        print("1. Start your Flask app: python app.py")
        print("2. In a new terminal, run: lt --port 5000")
        print("3. Share the generated URL with others")
        print("\n💡 LocalTunnel URLs look like: https://random-name.loca.lt")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up LocalTunnel: {e}")
        print("💡 Try running the command manually: npm install -g localtunnel")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def run_localtunnel():
    """Run LocalTunnel on port 5000"""
    try:
        print("🌐 Starting LocalTunnel on port 5000...")
        print("📝 Your public URL will be displayed below:")
        print("💡 Press Ctrl+C to stop sharing\n")

        # Run lt command
        subprocess.run(['lt', '--port', '5000'], check=True)

    except KeyboardInterrupt:
        print("\n🛑 LocalTunnel stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running LocalTunnel: {e}")
        print("💡 Make sure your Flask app is running on port 5000")
    except FileNotFoundError:
        print("❌ LocalTunnel not found. Run 'python localtunnel_setup.py' first")

def manual_setup_instructions():
    """Print manual setup instructions"""
    print("\n📖 Manual Setup Instructions for LocalTunnel:")
    print("=" * 50)
    print("1. Install Node.js from: https://nodejs.org/")
    print("2. Open Command Prompt/Terminal")
    print("3. Run: npm install -g localtunnel")
    print("4. Start your Flask app: python app.py")
    print("5. In new terminal: lt --port 5000")
    print("6. Share the generated URL!")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_localtunnel()
    elif len(sys.argv) > 1 and sys.argv[1] == "manual":
        manual_setup_instructions()
    else:
        success = setup_localtunnel()
        if not success:
            manual_setup_instructions()
