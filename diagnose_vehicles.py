import jaydebeapi
import os
import traceback
from database_manager_hybrid import db_manager

def diagnose_database():
    """Comprehensive diagnosis of vehicle registration issue"""
    
    print("=== DATABASE DIAGNOSIS ===")
    
    try:
        # Check if vehicles table exists
        print("\n1. Checking vehicles table existence...")
        try:
            schema = db_manager.get_table_schema('vehicles')
            if schema:
                print("✓ Vehicles table exists")
                print("   Columns:", schema)
            else:
                print("✗ Vehicles table not found")
        except Exception as e:
            print("✗ Error checking vehicles table:", str(e))
        
        # Check if members table exists
        print("\n2. Checking members table existence...")
        try:
            schema = db_manager.get_table_schema('members')
            if schema:
                print("✓ Members table exists")
                print("   Columns:", schema)
            else:
                print("✗ Members table not found")
        except Exception as e:
            print("✗ Error checking members table:", str(e))
        
        # Check actual data
        print("\n3. Checking actual data...")
        
        # Check members
        try:
            members = db_manager.execute_query("SELECT MemberID, Username, FirstName, LastName FROM members")
            print(f"   Members found: {len(members)}")
            for member in members:
                print(f"   - ID: {member[0]}, Username: {member[1]}, Name: {member[2]} {member[3]}")
        except Exception as e:
            print("   Error checking members:", str(e))
        
        # Check vehicles
        try:
            vehicles = db_manager.execute_query("SELECT * FROM vehicles")
            print(f"   Vehicles found: {len(vehicles)}")
            for vehicle in vehicles:
                print(f"   - ID: {vehicle[0]}, MemberID: {vehicle[1]}, Make: {vehicle[2]}, Model: {vehicle[3]}, Year: {vehicle[4]}, License: {vehicle[6]}")
        except Exception as e:
            print("   Error checking vehicles:", str(e))
        
        # Check permissions
        try:
            permissions = db_manager.execute_query("SELECT * FROM permissions")
            print(f"   Permissions entries: {len(permissions)}")
            for perm in permissions:
                print(f"   - MemberID: {perm[1]}, EditMembers: {perm[2]}, PostEvents: {perm[3]}, ManageVehicles: {perm[4]}")
        except Exception as e:
            print("   Error checking permissions:", str(e))
        
        # Check for any database errors
        print("\n4. Checking for database errors...")
        try:
            # Test a simple query
            test = db_manager.execute_query("SELECT 1")
            print("✓ Database connection working")
        except Exception as e:
            print("✗ Database connection error:", str(e))
        
        print("\n=== DIAGNOSIS COMPLETE ===")
        
    except Exception as e:
        print("Fatal error during diagnosis:", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database()
