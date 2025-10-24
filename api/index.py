import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    raise

# Vercel expects the Flask app to be named 'app'
# This file serves as the entry point for Vercel
