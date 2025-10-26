import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteDatabaseManager:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        # Use local AppData directory instead of OneDrive to avoid sync issues
        local_appdata = os.path.join(os.path.expanduser('~'), 'AppData', 'Local')
        db_dir = os.path.join(local_appdata, 'CarMeetCommunity')
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, 'carmeet_community.db')
        self.initialize_database()

    def initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Create members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username TEXT UNIQUE NOT NULL,
                    Password TEXT NOT NULL,
                    Email TEXT UNIQUE NOT NULL,
                    FirstName TEXT NOT NULL,
                    LastName TEXT NOT NULL,
                    Phone TEXT,
                    Bio TEXT,
                    ProfilePicture TEXT,
                    Location TEXT,
                    JoinDate TEXT DEFAULT CURRENT_DATE
                )
            ''')

            # Create permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    PermissionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    MemberID INTEGER NOT NULL,
                    CanEditMembers INTEGER DEFAULT 0,
                    CanPostEvents INTEGER DEFAULT 0,
                    CanManageVehicles INTEGER DEFAULT 0,
                    FOREIGN KEY (MemberID) REFERENCES members (MemberID)
                )
            ''')

            # Create vehicles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    MemberID INTEGER NOT NULL,
                    Make TEXT NOT NULL,
                    Model TEXT NOT NULL,
                    Year INTEGER NOT NULL,
                    Color TEXT NOT NULL,
                    LicensePlate TEXT UNIQUE NOT NULL,
                    Description TEXT,
                    DateAdded TEXT DEFAULT CURRENT_DATE,
                    FOREIGN KEY (MemberID) REFERENCES members (MemberID)
                )
            ''')

            # Create events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Description TEXT NOT NULL,
                    Location TEXT NOT NULL,
                    EventDate TEXT NOT NULL,
                    EventTime TEXT,
                    MaxAttendees INTEGER DEFAULT 50,
                    CreatedBy INTEGER NOT NULL,
                    CreatedDate TEXT DEFAULT CURRENT_DATE,
                    PlaceID INTEGER,
                    FOREIGN KEY (CreatedBy) REFERENCES members (MemberID)
                )
            ''')

            # Create places table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS places (
                    PlaceID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    Type TEXT NOT NULL,
                    Description TEXT,
                    Latitude REAL,
                    Longitude REAL,
                    AddedBy INTEGER NOT NULL,
                    AddedDate TEXT DEFAULT CURRENT_DATE,
                    FOREIGN KEY (AddedBy) REFERENCES members (MemberID)
                )
            ''')

            # Create tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
                    EventID INTEGER NOT NULL,
                    MemberID INTEGER NOT NULL,
                    PurchaseDate TEXT DEFAULT CURRENT_DATE,
                    Price REAL DEFAULT 0.0,
                    Status TEXT DEFAULT 'valid',
                    QRCode TEXT,
                    FOREIGN KEY (EventID) REFERENCES events (EventID),
                    FOREIGN KEY (MemberID) REFERENCES members (MemberID)
                )
            ''')

            # Create event_attendees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_attendees (
                    AttendeeID INTEGER PRIMARY KEY AUTOINCREMENT,
                    EventID INTEGER NOT NULL,
                    MemberID INTEGER NOT NULL,
                    RegistrationDate TEXT DEFAULT CURRENT_DATE,
                    FOREIGN KEY (EventID) REFERENCES events (EventID),
                    FOREIGN KEY (MemberID) REFERENCES members (MemberID),
                    UNIQUE(EventID, MemberID)
                )
            ''')

            conn.commit()
            logger.info("Database tables initialized successfully")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign keys for this connection
            conn.execute("PRAGMA foreign_keys = ON")
            logger.info("SQLite database connection established")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.info("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a query with proper error handling"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def table_exists(self, table_name):
        """Check if a table exists"""
        try:
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                [table_name]
            )
            return len(result) > 0
        except:
            return False

    def check_table_exists(self, table_name):
        """Check if a table exists (alias for table_exists)"""
        return self.table_exists(table_name)

    def register_user(self, username, email, password, first_name, last_name):
        """Register a new user"""
        try:
            # Check if user already exists
            existing = self.execute_query(
                "SELECT * FROM members WHERE Username = ? OR Email = ?",
                [username, email]
            )

            if existing:
                return {'success': False, 'error': 'Username or email already exists'}

            # Insert new user
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)

            result = self.execute_query(
                "INSERT INTO members (Username, Password, Email, FirstName, LastName) VALUES (?, ?, ?, ?, ?)",
                [username, hashed_password, email, first_name, last_name]
            )

            if result:
                # Get the newly created user ID
                user = self.execute_query(
                    "SELECT MemberID FROM members WHERE Username = ?",
                    [username]
                )

                if user:
                    user_id = user[0][0]

                    # Create default permissions
                    self.execute_query(
                        "INSERT INTO permissions (MemberID, CanEditMembers, CanPostEvents, CanManageVehicles) VALUES (?, 0, 0, 0)",
                        [user_id]
                    )

                    return {'success': True, 'user_id': user_id}

            return {'success': False, 'error': 'Failed to create user'}

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}

# Global database manager instance
db_manager = SQLiteDatabaseManager()
