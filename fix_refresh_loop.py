#!/usr/bin/env python3
"""
Fix for refresh loop issue in the Flask application
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def fix_refresh_loop():
    """
    Fix the refresh loop issue by modifying the login_required decorator
    and adding proper redirect handling
    """
    
    # Create a backup of the original app.py
    with open('app.py', 'r') as f:
        original_content = f.read()
    
    with open('app_backup_refresh.py', 'w') as f:
        f.write(original_content)
    
    # Fix the login_required decorator to prevent redirect loops
    fixed_content = original_content.replace(
        '''def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking login for {request.endpoint}, user_id in session: {'user_id' in session}")
        if 'user_id' not in session:
            logger.info(f"Redirecting to login from {request.endpoint}")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function''',
        '''def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking login for {request.endpoint}, user_id in session: {'user_id' in session}")
        if 'user_id' not in session:
            # Prevent redirect loop by checking if we're already on login page
            if request.endpoint == 'login':
                return f(*args, **kwargs)
            logger.info(f"Redirecting to login from {request.endpoint}")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function'''
    )
    
    # Also fix the login route to prevent redirect loops
    fixed_content = fixed_content.replace(
        '''    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        try:
            user = db_manager.execute_query(
                "SELECT * FROM members WHERE Username = ?",
                [username]
            )
            
            if user and check_password_hash(user[0][2], password):
                session['user_id'] = user[0][0]
                session['username'] = user[0][1]
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')''',
        '''    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        try:
            user = db_manager.execute_query(
                "SELECT * FROM members WHERE Username = ?",
                [username]
            )
            
            if user and check_password_hash(user[0][2], password):
                session['user_id'] = user[0][0]
                session['username'] = user[0][1]
                flash('Login successful!', 'success')
                # Check if there's a next URL parameter
                next_url = request.args.get('next')
                if next_url and next_url != url_for('login') and next_url != url_for('logout'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')'''
    )
    
    # Write the fixed content back
    with open('app.py', 'w') as f:
        f.write(fixed_content)
    
    print("✅ Refresh loop fix applied successfully!")
    print("📁 Backup saved as app_backup_refresh.py")

if __name__ == "__main__":
    fix_refresh_loop()
