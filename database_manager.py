import jaydebeapi
import os
import logging
from contextlib import contextmanager
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.current_dir, 'CarMeetCommunity.accdb')
        self.ucanaccess_path = os.path.join(self.current_dir, 'ucanaccess-5.0.1.jar')
        self.lib_dir = os.path.join(self.current_dir, 'lib')
        
    def get_connection_string(self):
        """Build complete classpath for UCanAccess"""
        classpath = [
            self.ucanaccess_path,
            os.path.join(self.lib_dir, 'commons-lang3-3.8.1.jar'),
            os.path.join(self.lib_dir, 'commons-logging-1.2.jar'),
            os.path.join(self.lib_dir, 'hsqldb-2.5.0.jar'),
            os.path.join(self.lib_dir, 'jackcess-3.0.1.jar')
        ]
        return os.pathsep.join(classpath)
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections with proper error handling"""
        conn = None
        try:
            jdbc_url = f"jdbc:ucanaccess://{self.db_path}"
            conn = jaydebeapi.connect(
                "net.ucanaccess.jdbc.UcanaccessDriver",
                jdbc_url,
                [],
                self.get_connection_string()
            )
            logger.info("Database connection established successfully")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                    logger.info("Database connection closed")
                except Exception as e:
                    logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a query with proper error handling and logging"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    logger.info(f"Query result: {result}")
                    return result
                else:
                    conn.commit()
                    logger.info(f"Query executed successfully: {query}")
                    return True
                    
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def check_table_exists(self, table_name):
        """Check if a table exists in the database"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name} WHERE 1=0")
                return True
        except:
            return False
    
    def get_table_schema(self, table_name):
        """Get table schema information"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name} WHERE 1=0")
                columns = [desc[0] for desc in cursor.description]
                return columns
        except Exception as e:
            logger.error(f"Error getting schema for {table_name}: {e}")
            return []
    
    def register_user(self, username, email, password, first_name, last_name):
        """Register a new user with comprehensive error handling"""
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
            
            insert_query = """
                INSERT INTO members (Username, Password, Email, FirstName, LastName, JoinDate)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            result = self.execute_query(
                insert_query,
                [username, hashed_password, email, first_name, last_name, current_date]
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
db_manager = DatabaseManager()
