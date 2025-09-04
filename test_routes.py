#!/usr/bin/env python3
"""
Simple route testing script for deployment verification
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_routes():
    """Test basic Flask routes"""
    with app.test_client() as client:
        # Test index route
        response = client.get('/')
        print(f"✅ Index route: {response.status_code}")

        # Test login route
        response = client.get('/login')
        print(f"✅ Login route: {response.status_code}")

        # Test register route
        response = client.get('/register')
        print(f"✅ Register route: {response.status_code}")

        print("✅ All basic routes responding correctly")

if __name__ == "__main__":
    test_routes()
