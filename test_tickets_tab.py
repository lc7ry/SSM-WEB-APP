#!/usr/bin/env python3
"""
Test script to verify that the Tickets tab is visible in the admin dashboard.
"""

import requests
from flask import Flask
import sys
import os

# Add current directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_tickets_tab_visibility():
    """Test that the Tickets tab is visible in admin dashboard"""

    with app.test_client() as client:
        # First, register a test admin user
        print("Registering test admin user...")
        register_response = client.post('/register', data={
            'username': 'testadmin',
            'email': 'testadmin@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Admin'
        }, follow_redirects=True)

        if b'Registration successful' not in register_response.data:
            print("Registration failed, trying login...")
        else:
            print("Registration successful")

        # Login as admin
        print("Logging in as admin...")
        login_response = client.post('/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)

        if b'Login successful' not in login_response.data and b'Welcome' not in login_response.data:
            print("Login failed")
            return False

        print("Login successful")

        # Access dashboard
        print("Accessing dashboard...")
        dashboard_response = client.get('/dashboard')

        if dashboard_response.status_code != 200:
            print(f"Dashboard access failed with status {dashboard_response.status_code}")
            return False

        dashboard_html = dashboard_response.data.decode('utf-8')

        # Check if Tickets tab is present and not hidden
        if 'data-tab="tickets"' in dashboard_html:
            if 'style="display:none;"' in dashboard_html:
                print("❌ FAIL: Tickets tab is still hidden with display:none")
                return False
            else:
                print("✅ PASS: Tickets tab is visible (no display:none found)")
                return True
        else:
            print("❌ FAIL: Tickets tab data-tab attribute not found")
            return False

if __name__ == '__main__':
    print("Testing Tickets tab visibility in admin dashboard...")
    success = test_tickets_tab_visibility()
    if success:
        print("\n🎉 Test passed! The Tickets tab is now visible for admins.")
    else:
        print("\n💥 Test failed! The Tickets tab is still hidden.")
    sys.exit(0 if success else 1)
