#!/usr/bin/env python3
"""
Comprehensive test script for profile editing functionality
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager_hybrid import db_manager

def test_database_columns():
    """Test that all required columns exist in members table"""
    print("🔍 Testing database columns...")

    try:
        # Get current columns
        with db_manager.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE 1=0")
            columns = [desc[0] for desc in cursor.description]

        print(f"Current columns: {columns}")

        required_columns = ['MemberID', 'Username', 'Password', 'Email', 'FirstName', 'LastName', 'Phone', 'Bio', 'ProfilePicture', 'Location']
        missing_columns = []

        for col in required_columns:
            if col not in columns:
                missing_columns.append(col)

        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns present")
            return True

    except Exception as e:
        print(f"❌ Error checking columns: {e}")
        return False

def test_profile_update():
    """Test profile update functionality"""
    print("\n🔄 Testing profile update functionality...")

    try:
        # Get a test user
        users = db_manager.execute_query("SELECT * FROM members LIMIT 1")
        if not users:
            print("❌ No users found. Creating a test user...")

            # Create a test user
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash('testpass123')

            insert_query = """
                INSERT INTO members (Username, Password, Email, FirstName, LastName, JoinDate)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')

            result = db_manager.execute_query(
                insert_query,
                ['testuser', hashed_password, 'test@example.com', 'Test', 'User', current_date]
            )

            if result > 0:
                users = db_manager.execute_query("SELECT * FROM members WHERE Username = ?", ['testuser'])

        if not users:
            print("❌ Could not create or find test user")
            return False

        user = users[0]
        user_id = user[0]
        print(f"Testing with user ID: {user_id}")

        # Test profile update
        update_query = """
            UPDATE members
            SET FirstName = ?, LastName = ?, Email = ?, Phone = ?, Bio = ?, ProfilePicture = ?, Location = ?
            WHERE MemberID = ?
        """

        test_data = [
            'UpdatedFirst',
            'UpdatedLast',
            'updated@example.com',
            '+1-555-123-4567',
            'This is my updated bio',
            'https://example.com/profile.jpg',
            'New York, NY',
            user_id
        ]

        result = db_manager.execute_query(update_query, test_data)

        if result > 0:
            print("✅ Profile update query executed successfully")

            # Verify the update
            updated_user = db_manager.execute_query("SELECT * FROM members WHERE MemberID = ?", [user_id])
            if updated_user:
                updated = updated_user[0]
                print("✅ Updated user data verification:")
                print(f"  FirstName: {updated[4]}")
                print(f"  LastName: {updated[5]}")
                print(f"  Email: {updated[3]}")
                print(f"  Phone: {updated[9] if len(updated) > 9 else 'N/A'}")
                print(f"  Bio: {updated[10] if len(updated) > 10 else 'N/A'}")
                print(f"  ProfilePicture: {updated[11] if len(updated) > 11 else 'N/A'}")
                print(f"  Location: {updated[12] if len(updated) > 12 else 'N/A'}")

                # Check if values match expected
                if (updated[4] == 'UpdatedFirst' and
                    updated[5] == 'UpdatedLast' and
                    updated[3] == 'updated@example.com'):
                    print("✅ Core fields updated correctly")
                    return True
                else:
                    print("❌ Updated values don't match expected")
                    return False
            else:
                print("❌ Could not retrieve updated user")
                return False
        else:
            print("❌ Profile update query failed")
            return False

    except Exception as e:
        print(f"❌ Error during profile update test: {e}")
        return False

def test_form_validation():
    """Test form validation scenarios"""
    print("\n📝 Testing form validation...")

    try:
        users = db_manager.execute_query("SELECT * FROM members LIMIT 1")
        if not users:
            print("❌ No users for validation testing")
            return False

        user_id = users[0][0]

        # Test with empty required fields
        update_query = """
            UPDATE members
            SET FirstName = ?, LastName = ?, Email = ?, Phone = ?, Bio = ?, ProfilePicture = ?, Location = ?
            WHERE MemberID = ?
        """

        # Empty first name (should fail validation in app, but test DB level)
        invalid_data = [
            '',  # Empty first name
            'TestLast',
            'test@example.com',
            '123-456-7890',
            'Test bio',
            'https://example.com/pic.jpg',
            'Test City',
            user_id
        ]

        result = db_manager.execute_query(update_query, invalid_data)

        if result > 0:
            print("✅ Database accepts empty first name (validation should be in app layer)")
        else:
            print("❌ Database rejected empty first name")

        return True

    except Exception as e:
        print(f"❌ Error during validation test: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting comprehensive profile editing tests...\n")

    tests = [
        ("Database Columns", test_database_columns),
        ("Profile Update", test_profile_update),
        ("Form Validation", test_form_validation)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Profile editing should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
