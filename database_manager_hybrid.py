import os
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridDatabaseManager:
    """
    Database manager that uses PostgreSQL for production (Netlify) and SQLite for development
    """

    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # Check if we're in Vercel/Netlify environment with PostgreSQL
        database_url = os.environ.get('DATABASE_URL') or os.environ.get('NETLIFY_DATABASE_URL')

        if database_url and 'postgres' in database_url:
            try:
                from database_manager_postgres import PostgreSQLDatabaseManager
                self.db_manager = PostgreSQLDatabaseManager(database_url)
                self.db_type = 'postgres'
                logger.info("Using PostgreSQL database manager (Vercel/Netlify)")
            except ImportError as e:
                logger.warning(f"PostgreSQL manager not available ({e}), falling back to SQLite")
                from database_manager_sqlite import SQLiteDatabaseManager
                self.db_manager = SQLiteDatabaseManager()
                self.db_type = 'sqlite'
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed ({e}), falling back to SQLite")
                from database_manager_sqlite import SQLiteDatabaseManager
                self.db_manager = SQLiteDatabaseManager()
                self.db_type = 'sqlite'
        else:
            # Use SQLite for development/local
            from database_manager_sqlite import SQLiteDatabaseManager
            self.db_manager = SQLiteDatabaseManager()
            self.db_type = 'sqlite'
            logger.info("Using SQLite database manager (development)")

    def execute_query(self, query, params=None):
        """Execute a query using the appropriate database manager"""
        return self.db_manager.execute_query(query, params)

    def check_table_exists(self, table_name):
        """Check if a table exists"""
        return self.db_manager.check_table_exists(table_name)

    def table_exists(self, table_name):
        """Alias for check_table_exists for compatibility"""
        return self.check_table_exists(table_name)

    def register_user(self, username, email, password, first_name, last_name):
        """Register a new user"""
        return self.db_manager.register_user(username, email, password, first_name, last_name)

    @contextmanager
    def get_db_connection(self):
        """Get database connection"""
        with self.db_manager.get_db_connection() as conn:
            yield conn

    # Enhanced methods for new features
    def get_vehicle_photos(self, vehicle_id):
        """Get photos for a specific vehicle"""
        return self.execute_query("SELECT * FROM vehicle_photos WHERE VehicleID = ? ORDER BY IsPrimary DESC, UploadDate DESC", (vehicle_id,))

    def add_vehicle_photo(self, vehicle_id, photo_url, caption=None, is_primary=False):
        """Add a photo to a vehicle"""
        return self.execute_query(
            "INSERT INTO vehicle_photos (VehicleID, PhotoURL, Caption, IsPrimary) VALUES (?, ?, ?, ?)",
            (vehicle_id, photo_url, caption, is_primary)
        )

    def get_event_rsvps(self, event_id):
        """Get RSVPs for a specific event"""
        return self.execute_query("SELECT * FROM event_rsvps WHERE EventID = ? ORDER BY RSVPDate DESC", (event_id,))

    def add_event_rsvp(self, event_id, user_email, user_name=None, phone=None, attendees=1, notes=None):
        """Add an RSVP to an event"""
        return self.execute_query(
            "INSERT INTO event_rsvps (EventID, UserEmail, UserName, Phone, Attendees, Notes) VALUES (?, ?, ?, ?, ?, ?)",
            (event_id, user_email, user_name, phone, attendees, notes)
        )

    def get_blog_posts(self, limit=10, offset=0, category=None, featured_only=False):
        """Get blog posts with optional filtering"""
        query = "SELECT * FROM blog_posts WHERE Published = 1"
        params = []

        if category:
            query += " AND Category = ?"
            params.append(category)

        if featured_only:
            query += " AND Featured = 1"

        query += " ORDER BY CreatedDate DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return self.execute_query(query, params)

    def get_blog_post(self, post_id):
        """Get a specific blog post"""
        return self.execute_query("SELECT * FROM blog_posts WHERE PostID = ? AND Published = 1", (post_id,))

    def add_blog_post(self, title, content, author_id, category=None, tags=None, featured=False):
        """Add a new blog post"""
        return self.execute_query(
            "INSERT INTO blog_posts (Title, Content, AuthorID, Category, Tags, Featured) VALUES (?, ?, ?, ?, ?, ?)",
            (title, content, author_id, category, tags, featured)
        )

    def get_comments(self, post_type, post_id):
        """Get comments for a post"""
        return self.execute_query(
            "SELECT c.*, m.FirstName, m.LastName FROM comments c JOIN members m ON c.AuthorID = m.MemberID WHERE c.PostType = ? AND c.PostID = ? ORDER BY c.CreatedDate ASC",
            (post_type, post_id)
        )

    def add_comment(self, content, author_id, post_type, post_id, parent_comment_id=None):
        """Add a comment to a post"""
        return self.execute_query(
            "INSERT INTO comments (Content, AuthorID, PostType, PostID, ParentCommentID) VALUES (?, ?, ?, ?, ?)",
            (content, author_id, post_type, post_id, parent_comment_id)
        )

    def toggle_like(self, user_id, post_type, post_id):
        """Toggle like on a post"""
        # Check if like exists
        existing = self.execute_query(
            "SELECT LikeID FROM likes WHERE UserID = ? AND PostType = ? AND PostID = ?",
            (user_id, post_type, post_id)
        )

        if existing:
            # Remove like
            self.execute_query("DELETE FROM likes WHERE LikeID = ?", (existing[0][0],))
            return False  # Like removed
        else:
            # Add like
            self.execute_query("INSERT INTO likes (UserID, PostType, PostID) VALUES (?, ?, ?)", (user_id, post_type, post_id))
            return True  # Like added

    def get_user_favorites(self, user_id, item_type=None):
        """Get user's favorites"""
        if item_type:
            return self.execute_query("SELECT * FROM user_favorites WHERE UserID = ? AND ItemType = ? ORDER BY CreatedDate DESC", (user_id, item_type))
        else:
            return self.execute_query("SELECT * FROM user_favorites WHERE UserID = ? ORDER BY CreatedDate DESC", (user_id,))

    def toggle_favorite(self, user_id, item_type, item_id):
        """Toggle favorite status"""
        existing = self.execute_query(
            "SELECT FavoriteID FROM user_favorites WHERE UserID = ? AND ItemType = ? AND ItemID = ?",
            (user_id, item_type, item_id)
        )

        if existing:
            self.execute_query("DELETE FROM user_favorites WHERE FavoriteID = ?", (existing[0][0],))
            return False
        else:
            self.execute_query("INSERT INTO user_favorites (UserID, ItemType, ItemID) VALUES (?, ?, ?)", (user_id, item_type, item_id))
            return True

    def follow_user(self, follower_id, following_id):
        """Follow a user"""
        try:
            self.execute_query("INSERT INTO follows (FollowerID, FollowingID) VALUES (?, ?)", (follower_id, following_id))
            return True
        except:
            return False  # Already following

    def unfollow_user(self, follower_id, following_id):
        """Unfollow a user"""
        self.execute_query("DELETE FROM follows WHERE FollowerID = ? AND FollowingID = ?", (follower_id, following_id))
        return True

    def get_followers(self, user_id):
        """Get user's followers"""
        return self.execute_query(
            "SELECT m.* FROM follows f JOIN members m ON f.FollowerID = m.MemberID WHERE f.FollowingID = ?",
            (user_id,)
        )

    def get_following(self, user_id):
        """Get users that user is following"""
        return self.execute_query(
            "SELECT m.* FROM follows f JOIN members m ON f.FollowingID = m.MemberID WHERE f.FollowerID = ?",
            (user_id,)
        )

    def add_notification(self, user_id, notification_type, title, message, related_type=None, related_id=None):
        """Add a notification for a user"""
        return self.execute_query(
            "INSERT INTO notifications (UserID, Type, Title, Message, RelatedType, RelatedID) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, notification_type, title, message, related_type, related_id)
        )

    def get_notifications(self, user_id, unread_only=False):
        """Get user's notifications"""
        query = "SELECT * FROM notifications WHERE UserID = ?"
        if unread_only:
            query += " AND IsRead = 0"
        query += " ORDER BY CreatedDate DESC"
        return self.execute_query(query, (user_id,))

    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        self.execute_query("UPDATE notifications SET IsRead = 1 WHERE NotificationID = ?", (notification_id,))

    def log_activity(self, user_id, action, details=None, ip_address=None, user_agent=None):
        """Log user activity"""
        self.execute_query(
            "INSERT INTO user_activity_logs (UserID, Action, Details, IPAddress, UserAgent) VALUES (?, ?, ?, ?, ?)",
            (user_id, action, details, ip_address, user_agent)
        )

    def get_recent_activity(self, user_id=None, limit=20):
        """Get recent activity logs"""
        if user_id:
            return self.execute_query("SELECT * FROM user_activity_logs WHERE UserID = ? ORDER BY CreatedDate DESC LIMIT ?", (user_id, limit))
        else:
            return self.execute_query("SELECT * FROM user_activity_logs ORDER BY CreatedDate DESC LIMIT ?", (limit,))

# Global database manager instance
db_manager = HybridDatabaseManager()
