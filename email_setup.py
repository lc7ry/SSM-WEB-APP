#!/usr/bin/env python3
"""
Email Configuration Setup for Flask-Mail

This script helps you configure email settings for the forgot password feature.

For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an app password: https://support.google.com/accounts/answer/185833
3. Use your Gmail address as MAIL_USERNAME and the app password as MAIL_PASSWORD

For other email providers, check their SMTP settings.
"""

import os
from dotenv import load_dotenv

# Load existing environment variables if .env file exists
load_dotenv()

def setup_email_config():
    """Interactive setup for email configuration"""

    print("=== Flask-Mail Configuration Setup ===\n")

    print("This will help you configure email settings for password reset functionality.\n")

    # Get email provider
    print("Select your email provider:")
    print("1. Gmail")
    print("2. Outlook/Hotmail")
    print("3. Yahoo")
    print("4. Custom SMTP")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        # Gmail configuration
        mail_server = 'smtp.gmail.com'
        mail_port = '587'
        mail_use_tls = 'True'
        mail_use_ssl = 'False'

        print("\n=== Gmail Setup Instructions ===")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-factor authentication if not already enabled")
        print("3. Go to https://myaccount.google.com/apppasswords")
        print("4. Generate an app password for 'Flask App'")
        print("5. Use your Gmail address and the generated app password below\n")

    elif choice == '2':
        # Outlook configuration
        mail_server = 'smtp-mail.outlook.com'
        mail_port = '587'
        mail_use_tls = 'True'
        mail_use_ssl = 'False'
        print("\nFor Outlook, use your full email address and password.")

    elif choice == '3':
        # Yahoo configuration
        mail_server = 'smtp.mail.yahoo.com'
        mail_port = '587'
        mail_use_tls = 'True'
        mail_use_ssl = 'False'
        print("\nFor Yahoo, use your full email address and app password if 2FA is enabled.")

    elif choice == '4':
        # Custom SMTP
        mail_server = input("SMTP Server: ").strip()
        mail_port = input("SMTP Port (usually 587 or 465): ").strip()
        mail_use_tls = input("Use TLS? (True/False): ").strip()
        mail_use_ssl = input("Use SSL? (True/False): ").strip()

    else:
        print("Invalid choice. Exiting.")
        return

    # Get email credentials
    mail_username = input("Email address (your login email): ").strip()
    mail_password = input("Password/App Password: ").strip()
    mail_default_sender = input("Default sender email (usually same as username): ").strip() or mail_username

    # Create or update .env file
    env_content = f"""# Flask-Mail Configuration
MAIL_SERVER={mail_server}
MAIL_PORT={mail_port}
MAIL_USE_TLS={mail_use_tls}
MAIL_USE_SSL={mail_use_ssl}
MAIL_USERNAME={mail_username}
MAIL_PASSWORD={mail_password}
MAIL_DEFAULT_SENDER={mail_default_sender}

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
"""

    try:
        with open('.env', 'w') as f:
            f.write(env_content)

        print("\n✅ Configuration saved to .env file!")
        print("\n📧 To test the email configuration:")
        print("1. Make sure your .env file is in the same directory as app.py")
        print("2. Restart your Flask application")
        print("3. Try the forgot password feature with a valid email address")
        print("\n🔍 Check the application logs for any email sending errors.")

    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        print("\nManual setup:")
        print("Create a .env file in your project directory with the following content:")
        print(env_content)

if __name__ == '__main__':
    setup_email_config()
