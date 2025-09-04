import os
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridDatabaseManager:
    """
    Hybrid database manager that uses MS Access locally and SQLite for deployment
    """

    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.is_deployment = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER') == 'true'

        if self.is_deployment:
            # Use SQLite for deployment (Render, etc.)
            from database_manager_sqlite import SQLiteDatabaseManager
            self.db_manager = SQLiteDatabaseManager()
            logger.info("Using SQLite database manager for deployment")
        else:
            # Use MS Access for local development
            try:
                from database_manager import DatabaseManager
                self.db_manager = DatabaseManager()
                logger.info("Using MS Access database manager for local development")
            except ImportError as e:
                logger.warning(f"MS Access not available, falling back to SQLite: {e}")
                from database_manager_sqlite import SQLiteDatabaseManager
                self.db_manager = SQLiteDatabaseManager()

    def execute_query(self, query, params=None):
        """Execute a query using the appropriate database manager"""
        return self.db_manager.execute_query(query, params)

    def table_exists(self, table_name):
        """Check if a table exists"""
        return self.db_manager.table_exists(table_name)

    def register_user(self, username, email, password, first_name, last_name):
        """Register a new user"""
        return self.db_manager.register_user(username, email, password, first_name, last_name)

    @contextmanager
    def get_db_connection(self):
        """Get database connection"""
        with self.db_manager.get_db_connection() as conn:
            yield conn

# Global database manager instance
db_manager = HybridDatabaseManager()
