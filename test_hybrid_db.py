#!/usr/bin/env python3
"""
Test script to verify the hybrid database manager works correctly
"""
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager_hybrid import db_manager

def test_hybrid_manager():
    """Test the hybrid database manager"""
    print("🔧 Testing Hybrid Database Manager")
    print("=" * 40)

    try:
        # Test basic connection
        print("1. Testing database connection...")
        with db_manager.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"   ✅ Connection successful: {result}")

        # Test table existence
        print("\n2. Testing table existence...")
        tables_to_check = ['members', 'vehicles', 'events', 'places']
        for table in tables_to_check:
            exists = db_manager.table_exists(table)
            status = "✅" if exists else "❌"
            print(f"   {status} {table} table: {'exists' if exists else 'not found'}")

        # Test query execution
        print("\n3. Testing query execution...")
        try:
            # Simple count query
            result = db_manager.execute_query("SELECT COUNT(*) FROM members")
            print(f"   ✅ Members count query: {result[0][0] if result else 0} members")
        except Exception as e:
            print(f"   ❌ Query execution failed: {e}")

        # Test which database manager is being used
        print("\n4. Database manager type:")
        if hasattr(db_manager, 'db_manager'):
            manager_type = type(db_manager.db_manager).__name__
            print(f"   📊 Using: {manager_type}")

            if 'SQLite' in manager_type:
                print("   💡 SQLite mode (for deployment)")
            elif 'Database' in manager_type:
                print("   💡 MS Access mode (for local development)")
            else:
                print("   ❓ Unknown database type")

        print("\n" + "=" * 40)
        print("🎉 Hybrid database manager test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hybrid_manager()
    sys.exit(0 if success else 1)
