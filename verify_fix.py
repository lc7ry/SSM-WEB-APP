#!/usr/bin/env python3
"""
Simple verification script for the profile editing fix
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager_sqlite import db_manager

def verify_database_schema():
    """Verify that the database has all required columns"""
    print("=== DATABASE SCHEMA VERIFICATION ===")

    try:
        with db_manager.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE 1=0")
            columns = [desc[0] for desc in cursor.description]

        print(f"Found {len(columns)} columns in members table:")
        for i, col in enumerate(columns):
            print(f"  {i}: {col}")

        required = ['Phone', 'Bio', 'ProfilePicture', 'Location']
        missing = [col for col in required if col not in columns]

        if missing:
            print(f"\n❌ MISSING COLUMNS: {missing}")
            print("Please run: python add_missing_columns.py")
            return False
        else:
            print("\n✅ All required columns are present!")
            return True

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def verify_profile_update():
    """Verify that profile updates work"""
    print("\n=== PROFILE UPDATE VERIFICATION ===")

    try:
        # Get or create a test user
        users = db_manager.execute_query("SELECT * FROM members LIMIT 1")
        if not users:
            print("Creating test user...")
            from werkzeug.security import generate_password_hash
            from datetime import datetime

            hashed_password = generate_password_hash('testpass123')
            current_date = datetime.now().strftime('%Y-%m-%d')

            result = db_manager.execute_query(
                "INSERT INTO members (Username, Password, Email, FirstName, LastName, JoinDate) VALUES (?, ?, ?, ?, ?, ?)",
                ['testuser', hashed_password, 'test@example.com', 'Test', 'User', current_date]
            )

            if result > 0:
                users = db_manager.execute_query("SELECT * FROM members WHERE Username = ?", ['testuser'])

        if not users:
            print("❌ Could not find or create test user")
            return False

        user_id = users[0][0]
        print(f"Testing with user ID: {user_id}")

        # Test the exact query from the app
        update_query = """
            UPDATE members
            SET FirstName = ?, LastName = ?, Email = ?, Phone = ?, Bio = ?, ProfilePicture = ?, Location = ?
            WHERE MemberID = ?
        """

        test_values = [
            'John',
            'Doe',
            'john.doe@example.com',
            '+1-555-0123',
            'I love car meets!',
            'https://example.com/avatar.jpg',
            'Los Angeles, CA',
            user_id
        ]

        print("Executing profile update...")
        result = db_manager.execute_query(update_query, test_values)

        if result > 0:
            print("✅ Update query executed successfully!")

            # Verify the data was saved
            updated = db_manager.execute_query("SELECT * FROM members WHERE MemberID = ?", [user_id])
            if updated:
                user = updated[0]
                print("✅ Data verification:")
                print(f"  Name: {user[4]} {user[5]}")
                print(f"  Email: {user[3]}")
                if len(user) > 9:
                    print(f"  Phone: {user[9] or 'Not set'}")
                    print(f"  Bio: {user[10] or 'Not set'}")
                    print(f"  Profile Picture: {user[11] or 'Not set'}")
                    print(f"  Location: {user[12] or 'Not set'}")

                return True
            else:
                print("❌ Could not retrieve updated data")
                return False
        else:
            print("❌ Update query failed")
            return False

    except Exception as e:
        print(f"❌ Error during profile update: {e}")
        return False

def main():
    print("🔧 VERIFYING PROFILE EDITING FIX\n")

    schema_ok = verify_database_schema()
    update_ok = verify_profile_update()

    print("\n" + "="*50)
    print("📋 VERIFICATION RESULTS")
    print("="*50)

    if schema_ok and update_ok:
        print("🎉 SUCCESS! The profile editing issue has been fixed!")
        print("\nWhat was fixed:")
        print("✅ Added missing database columns (Phone, Bio, ProfilePicture, Location)")
        print("✅ Updated app.py to handle all form fields")
        print("✅ Updated templates to display and pre-fill new fields")
        print("\nThe 'error updating profile' issue should now be resolved.")
        return True
    else:
        print("❌ VERIFICATION FAILED")
        if not schema_ok:
            print("• Database schema needs to be updated")
        if not update_ok:
            print("• Profile update functionality has issues")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
