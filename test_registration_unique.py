#!/usr/bin/env python3
"""
Test script to reproduce the "attempt to write a readonly database" error during registration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager_hybrid import db_manager

def test_registration():
    """Test user registration"""
    print("Testing user registration...")

    try:
        # Test data - use unique values
        import time
        timestamp = str(int(time.time()))
        username = f"testuser{timestamp}"
        email = f"test{timestamp}@example.com"
        password = "testpass123"
        first_name = "Test"
        last_name = "User"

        print(f"Attempting to register user: {username}")

        # Attempt registration
        result = db_manager.register_user(username, email, password, first_name, last_name)

        print(f"Registration result: {result}")

        if result['success']:
            print("✅ Registration successful!")
        else:
            print(f"❌ Registration failed: {result['error']}")

    except Exception as e:
        print(f"❌ Exception during registration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()
