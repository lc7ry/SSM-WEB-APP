import sqlite3

def view_members():
    print('\n=== MEMBERS ===')
    conn = sqlite3.connect('carmeet_community.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MemberID, Username, FirstName, LastName, Email, JoinDate FROM members')
    members = cursor.fetchall()
    for member in members:
        print(f'ID: {member[0]}, Username: {member[1]}, Name: {member[2]} {member[3]}, Email: {member[4]}, Joined: {member[5]}')
    conn.close()

def view_vehicles():
    print('\n=== VEHICLES ===')
    conn = sqlite3.connect('carmeet_community.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.VehicleID, v.Make, v.Model, v.Year, v.Color, v.LicensePlate, m.Username
        FROM vehicles v
        JOIN members m ON v.MemberID = m.MemberID
    ''')
    vehicles = cursor.fetchall()
    for vehicle in vehicles:
        print(f'ID: {vehicle[0]}, {vehicle[1]} {vehicle[2]} {vehicle[3]}, Color: {vehicle[4]}, Plate: {vehicle[5]}, Owner: {vehicle[6]}')
    conn.close()

def view_events():
    print('\n=== EVENTS ===')
    conn = sqlite3.connect('carmeet_community.db')
    cursor = conn.cursor()
    cursor.execute('SELECT EventID, Title, Location, EventDate, MaxAttendees FROM events ORDER BY EventDate DESC')
    events = cursor.fetchall()
    for event in events:
        print(f'ID: {event[0]}, Title: {event[1]}, Location: {event[2]}, Date: {event[3]}, Max Attendees: {event[4]}')
    conn.close()

def view_places():
    print('\n=== PLACES ===')
    conn = sqlite3.connect('carmeet_community.db')
    cursor = conn.cursor()
    cursor.execute('SELECT PlaceID, Name, Address, Type FROM places')
    places = cursor.fetchall()
    for place in places:
        print(f'ID: {place[0]}, Name: {place[1]}, Address: {place[2]}, Type: {place[3]}')
    conn.close()

if __name__ == '__main__':
    print('=== DATABASE VIEWER ===')
    print('Choose what to view:')
    print('1. Members')
    print('2. Vehicles')
    print('3. Events')
    print('4. Places')
    print('5. All')

    choice = input('Enter your choice (1-5): ')

    if choice == '1':
        view_members()
    elif choice == '2':
        view_vehicles()
    elif choice == '3':
        view_events()
    elif choice == '4':
        view_places()
    elif choice == '5':
        view_members()
        view_vehicles()
        view_events()
        view_places()
    else:
        print('Invalid choice')

    # Always show permissions
    print('\n=== PERMISSIONS ===')
    conn = sqlite3.connect('carmeet_community.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.MemberID, m.Username, p.CanEditMembers, p.CanPostEvents, p.CanManageVehicles
        FROM members m
        LEFT JOIN permissions p ON m.MemberID = p.MemberID
    ''')
    permissions = cursor.fetchall()
    for perm in permissions:
        print(f'ID: {perm[0]}, Username: {perm[1]}, CanEditMembers: {perm[2]}, CanPostEvents: {perm[3]}, CanManageVehicles: {perm[4]}')
    conn.close()
