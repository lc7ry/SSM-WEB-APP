import sqlite3

# Connect to database
conn = sqlite3.connect('carmeet_community.db')
cursor = conn.cursor()

print('=== MEMBERS AND PERMISSIONS ===')

# Check members and their permissions
cursor.execute('''
    SELECT m.MemberID, m.Username, m.FirstName, m.LastName,
           p.CanEditMembers, p.CanPostEvents, p.CanManageVehicles
    FROM members m
    LEFT JOIN permissions p ON m.MemberID = p.MemberID
''')

members = cursor.fetchall()
for member in members:
    member_id, username, first, last, edit_members, post_events, manage_vehicles = member
    role = 'Admin' if edit_members else ('Moderator' if (post_events or manage_vehicles) else 'Member')
    print(f'{username} ({first} {last}) - Role: {role}')
    print(f'  Permissions: Edit Members={bool(edit_members)}, Post Events={bool(post_events)}, Manage Vehicles={bool(manage_vehicles)}')
    print()

conn.close()
