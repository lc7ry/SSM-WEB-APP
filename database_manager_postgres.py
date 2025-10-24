import psycopg2
import psycopg2.extras
import os
import logging
from contextlib import contextmanager
from datetime import datetime
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLDatabaseManager:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get('DATABASE_URL') or os.environ.get('NETLIFY_DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL or NETLIFY_DATABASE_URL environment variable is required for PostgreSQL")

        # Parse the database URL
        parsed = urlparse(self.database_url)
        self.db_config = {
            'host': parsed.hostname,
            'port': parsed.port,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/')
        }

        self.initialize_database()

    def initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Create members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    "MemberID" SERIAL PRIMARY KEY,
                    "Username" TEXT UNIQUE NOT NULL,
                    "Password" TEXT NOT NULL,
                    "Email" TEXT UNIQUE NOT NULL,
                    "FirstName" TEXT NOT NULL,
                    "LastName" TEXT NOT NULL,
                    "Phone" TEXT,
                    "Bio" TEXT,
                    "ProfilePicture" TEXT,
                    "Location" TEXT,
                    "JoinDate" DATE DEFAULT CURRENT_DATE
                )
            ''')

            # Create permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    "PermissionID" SERIAL PRIMARY KEY,
                    "MemberID" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "CanEditMembers" BOOLEAN DEFAULT FALSE,
                    "CanPostEvents" BOOLEAN DEFAULT FALSE,
                    "CanManageVehicles" BOOLEAN DEFAULT FALSE
                )
            ''')

            # Create vehicles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id SERIAL PRIMARY KEY,
                    "MemberID" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "Make" TEXT NOT NULL,
                    "Model" TEXT NOT NULL,
                    "Year" INTEGER NOT NULL,
                    "Color" TEXT NOT NULL,
                    "LicensePlate" TEXT UNIQUE NOT NULL,
                    "Description" TEXT,
                    "DateAdded" DATE DEFAULT CURRENT_DATE
                )
            ''')

            # Create events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    "EventID" SERIAL PRIMARY KEY,
                    "Title" TEXT NOT NULL,
                    "Description" TEXT NOT NULL,
                    "Location" TEXT NOT NULL,
                    "EventDate" DATE NOT NULL,
                    "EventTime" TIME,
                    "MaxAttendees" INTEGER DEFAULT 50,
                    "CreatedBy" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "CreatedDate" DATE DEFAULT CURRENT_DATE,
                    "PlaceID" INTEGER
                )
            ''')

            # Create places table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS places (
                    "PlaceID" SERIAL PRIMARY KEY,
                    "Name" TEXT NOT NULL,
                    "Address" TEXT NOT NULL,
                    "Type" TEXT NOT NULL,
                    "Description" TEXT,
                    "Latitude" REAL,
                    "Longitude" REAL,
                    "AddedBy" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "AddedDate" DATE DEFAULT CURRENT_DATE
                )
            ''')

            # Create tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    "TicketID" SERIAL PRIMARY KEY,
                    "EventID" INTEGER NOT NULL REFERENCES events("EventID"),
                    "MemberID" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "PurchaseDate" DATE DEFAULT CURRENT_DATE,
                    "Price" REAL DEFAULT 0.0,
                    "Status" TEXT DEFAULT 'valid',
                    "QRCode" TEXT
                )
            ''')

            # Create event_attendees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_attendees (
                    "AttendeeID" SERIAL PRIMARY KEY,
                    "EventID" INTEGER NOT NULL REFERENCES events("EventID"),
                    "MemberID" INTEGER NOT NULL REFERENCES members("MemberID"),
                    "RegistrationDate" DATE DEFAULT CURRENT_DATE,
                    UNIQUE("EventID", "MemberID")
                )
            ''')

            conn.commit()
            logger.info("PostgreSQL database tables initialized successfully")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("PostgreSQL database connection established")
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
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    # Convert to list of dicts for consistency with SQLite
                    return [dict(row) for row in result]
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
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                [table_name.lower()]
            )
            return result[0]['exists'] if result else False
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
                'SELECT * FROM members WHERE "Username" = %s OR "Email" = %s',
                [username, email]
            )

            if existing:
                return {'success': False, 'error': 'Username or email already exists'}

            # Insert new user
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)

            result = self.execute_query(
                'INSERT INTO members ("Username", "Password", "Email", "FirstName", "LastName") VALUES (%s, %s, %s, %s, %s)',
                [username, hashed_password, email, first_name, last_name]
            )

            if result:
                # Get the newly created user ID
                user = self.execute_query(
                    'SELECT "MemberID" FROM members WHERE "Username" = %s',
                    [username]
                )

                if user:
                    user_id = user[0]['MemberID']

                    # Create default permissions
                    self.execute_query(
                        'INSERT INTO permissions ("MemberID", "CanEditMembers", "CanPostEvents", "CanManageVehicles") VALUES (%s, FALSE, FALSE, FALSE)',
                        [user_id]
                    )

                    return {'success': True, 'user_id': user_id}

            return {'success': False, 'error': 'Failed to create user'}

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}

# Global database manager instance
# Note: This will be initialized when the class is instantiated in hybrid manager
# db_manager = PostgreSQLDatabaseManager()
