import jaydebeapi
import os

# Database configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'CarMeetCommunity.accdb')
ucanaccess_path = os.path.join(current_dir, 'ucanaccess-5.0.1.jar')
lib_dir = os.path.join(current_dir, 'lib')

# Build classpath
classpath = [
    ucanaccess_path,
    os.path.join(lib_dir, 'commons-lang3-3.8.1.jar'),
    os.path.join(lib_dir, 'commons-logging-1.2.jar'),
    os.path.join(lib_dir, 'hsqldb-2.5.0.jar'),
    os.path.join(lib_dir, 'jackcess-3.0.1.jar')
]

classpath_str = os.pathsep.join(classpath)
jdbc_url = f"jdbc:ucanaccess://{db_path}"

def check_and_fix_database():
    """Check database structure and create missing tables"""
    try:
        conn = jaydebeapi.connect(
            "net.ucanaccess.jdbc.UcanaccessDriver",
            jdbc_url,
            [],
            classpath_str
        )
        
        cursor = conn.cursor()
        
        # Check if members table exists
        try:
            cursor.execute("SELECT 1 FROM members WHERE 1=0")
            print("✓ Members table exists")
        except:
            print("✗ Members table missing - creating...")
            
            # Create members table
            cursor.execute("""
                CREATE TABLE members (
                    MemberID AUTOINCREMENT PRIMARY KEY,
                    Username VARCHAR(50) NOT NULL UNIQUE,
                    Password VARCHAR(255) NOT NULL,
                    Email VARCHAR(100) NOT NULL UNIQUE,
                    FirstName VARCHAR(50),
                    LastName VARCHAR(50),
                    JoinDate DATETIME DEFAULT NOW(),
                    LastLogin DATETIME,
                    IsActive YESNO DEFAULT YES
                )
            """)
            print("✓ Members table created")
        
        # Check if permissions table exists
        try:
            cursor.execute("SELECT 1 FROM permissions WHERE 1=0")
            print("✓ Permissions table exists")
        except:
            print("✗ Permissions table missing - creating...")
            
            cursor.execute("""
                CREATE TABLE permissions (
                    PermissionID AUTOINCREMENT PRIMARY KEY,
                    MemberID INTEGER NOT NULL,
                    CanEditMembers YESNO DEFAULT NO,
                    CanPostEvents YESNO DEFAULT NO,
                    CanManageVehicles YESNO DEFAULT NO
                )
            """)
            print("✓ Permissions table created")
        
        # Check if vehicles table exists
        try:
            cursor.execute("SELECT 1 FROM vehicles WHERE 1=0")
            print("✓ Vehicles table exists")
        except:
            print("✗ Vehicles table missing - creating...")
            
            cursor.execute("""
                CREATE TABLE vehicles (
                    VehicleID AUTOINCREMENT PRIMARY KEY,
                    MemberID INTEGER NOT NULL,
                    Make VARCHAR(50),
                    Model VARCHAR(50),
                    Year INTEGER,
                    Color VARCHAR(30),
                    LicensePlate VARCHAR(20),
                    Description TEXT,
                    DateAdded DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Vehicles table created")
        
        # Check if events table exists
        try:
            cursor.execute("SELECT 1 FROM events WHERE 1=0")
            print("✓ Events table exists")
        except:
            print("✗ Events table missing - creating...")
            
            cursor.execute("""
                CREATE TABLE events (
                    EventID AUTOINCREMENT PRIMARY KEY,
                    Title VARCHAR(100) NOT NULL,
                    Description TEXT,
                    EventDate DATETIME,
                    Location VARCHAR(255),
                    CreatedBy INTEGER,
                    CreatedDate DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Events table created")
        
        # Check if places table exists
        try:
            cursor.execute("SELECT 1 FROM places WHERE 1=0")
            print("✓ Places table exists")
        except:
            print("✗ Places table missing - creating...")
            
            cursor.execute("""
                CREATE TABLE places (
                    PlaceID AUTOINCREMENT PRIMARY KEY,
                    Name VARCHAR(100) NOT NULL,
                    Address VARCHAR(255),
                    Description TEXT,
                    Type VARCHAR(50),
                    AddedBy INTEGER,
                    AddedDate DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Places table created")
        
        conn.commit()
        conn.close()
        print("\n✅ Database structure fixed successfully!")
        print("You can now restart your Flask application.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing database structure...")
    check_and_fix_database()
