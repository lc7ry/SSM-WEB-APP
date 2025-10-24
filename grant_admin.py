import sqlite3

# Connect to database
conn = sqlite3.connect('carmeet_community.db')
cursor = conn.cursor()

print('=== GRANTING ADMIN PERMISSIONS ===')

# Username to make admin
username_to_admin = 'admin'

# Find the member
cursor.execute('SELECT MemberID FROM members WHERE Username = ?', (username_to_admin,))
result = cursor.fetchone()

if result:
    member_id = result[0]
    print(f'Found user "{username_to_admin}" with MemberID: {member_id}')

    # Check if permissions record exists
    cursor.execute('SELECT * FROM permissions WHERE MemberID = ?', (member_id,))
    existing_perm = cursor.fetchone()

    if existing_perm:
        # Update existing permissions
        cursor.execute('''
            UPDATE permissions
            SET CanEditMembers = 1, CanPostEvents = 1, CanManageVehicles = 1
            WHERE MemberID = ?
        ''', (member_id,))
        print(f'Updated permissions for {username_to_admin} to Admin')
    else:
        # Create new permissions record
        cursor.execute('''
            INSERT INTO permissions (MemberID, CanEditMembers, CanPostEvents, CanManageVehicles)
            VALUES (?, 1, 1, 1)
        ''', (member_id,))
        print(f'Created admin permissions for {username_to_admin}')

    conn.commit()
    print(f'✅ {username_to_admin} is now an Admin!')
    print('You can now access /manage_permissions to manage other users\' permissions.')
else:
    print(f'❌ Username "{username_to_admin}" not found in database')

conn.close()
