import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Vercel expects the Flask app to be named 'app'
# This file serves as the entry point for Vercel
