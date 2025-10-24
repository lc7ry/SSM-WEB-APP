#!/usr/bin/env python3
"""
Simple test to check if tickets tab is visible
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

with app.test_client() as client:
    # Register and login as admin
    client.post('/register', data={
        'username': 'testadmin',
        'email': 'testadmin@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'Admin'
    }, follow_redirects=True)

    from permissions_manager import PermissionManager
    PermissionManager.update_permissions(1, {'can_edit_members': True})

    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpass123'
    }, follow_redirects=True)

    # Get dashboard
    response = client.get('/dashboard')
    html = response.data.decode('utf-8')

    # Check for tickets tab
    if 'data-tab="tickets"' in html:
        print('✅ PASS: Tickets tab data-tab attribute found')
        if 'display:none' in html:
            print('❌ FAIL: Found display:none in HTML')
        else:
            print('✅ PASS: No display:none found')
    else:
        print('❌ FAIL: Tickets tab data-tab attribute not found')
