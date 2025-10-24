"""
Database Schema Updates for SuliStreetMeet Platform
This script handles the migration to add new tables and columns for enhanced features.
"""

import os
import logging
from database_manager_hybrid import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_new_tables():
    """Add new tables required for enhanced features"""

    # vehicle_photos table
    vehicle_photos_sqlite = '''
        CREATE TABLE IF NOT EXISTS vehicle_photos (
            PhotoID INTEGER PRIMARY KEY AUTOINCREMENT,
            VehicleID INTEGER NOT NULL,
            PhotoURL TEXT NOT NULL,
            Caption TEXT,
            IsPrimary INTEGER DEFAULT 0,
            UploadDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (VehicleID) REFERENCES vehicles (id)
        )
    '''

    vehicle_photos_postgres = '''
        CREATE TABLE IF NOT EXISTS vehicle_photos (
            "PhotoID" SERIAL PRIMARY KEY,
            "VehicleID" INTEGER NOT NULL REFERENCES vehicles (id),
            "PhotoURL" TEXT NOT NULL,
            "Caption" TEXT,
            "IsPrimary" BOOLEAN DEFAULT FALSE,
            "UploadDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # event_rsvps table
    event_rsvps_sqlite = '''
        CREATE TABLE IF NOT EXISTS event_rsvps (
            RSVP_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventID INTEGER NOT NULL,
            UserEmail TEXT NOT NULL,
            UserName TEXT,
            Phone TEXT,
            Attendees INTEGER DEFAULT 1,
            Notes TEXT,
            RSVPDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (EventID) REFERENCES events (EventID)
        )
    '''

    event_rsvps_postgres = '''
        CREATE TABLE IF NOT EXISTS event_rsvps (
            "RSVP_ID" SERIAL PRIMARY KEY,
            "EventID" INTEGER NOT NULL REFERENCES events ("EventID"),
            "UserEmail" TEXT NOT NULL,
            "UserName" TEXT,
            "Phone" TEXT,
            "Attendees" INTEGER DEFAULT 1,
            "Notes" TEXT,
            "RSVPDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # blog_posts table
    blog_posts_sqlite = '''
        CREATE TABLE IF NOT EXISTS blog_posts (
            PostID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Content TEXT NOT NULL,
            AuthorID INTEGER NOT NULL,
            Category TEXT,
            Tags TEXT,
            Featured INTEGER DEFAULT 0,
            Published INTEGER DEFAULT 0,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            UpdatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (AuthorID) REFERENCES members (MemberID)
        )
    '''

    blog_posts_postgres = '''
        CREATE TABLE IF NOT EXISTS blog_posts (
            "PostID" SERIAL PRIMARY KEY,
            "Title" TEXT NOT NULL,
            "Content" TEXT NOT NULL,
            "AuthorID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "Category" TEXT,
            "Tags" TEXT,
            "Featured" BOOLEAN DEFAULT FALSE,
            "Published" BOOLEAN DEFAULT FALSE,
            "CreatedDate" DATE DEFAULT CURRENT_DATE,
            "UpdatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # comments table
    comments_sqlite = '''
        CREATE TABLE IF NOT EXISTS comments (
            CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
            Content TEXT NOT NULL,
            AuthorID INTEGER NOT NULL,
            PostType TEXT NOT NULL,
            PostID INTEGER NOT NULL,
            ParentCommentID INTEGER,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (AuthorID) REFERENCES members (MemberID)
        )
    '''

    comments_postgres = '''
        CREATE TABLE IF NOT EXISTS comments (
            "CommentID" SERIAL PRIMARY KEY,
            "Content" TEXT NOT NULL,
            "AuthorID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "PostType" TEXT NOT NULL,
            "PostID" INTEGER NOT NULL,
            "ParentCommentID" INTEGER,
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # likes table
    likes_sqlite = '''
        CREATE TABLE IF NOT EXISTS likes (
            LikeID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            PostType TEXT NOT NULL,
            PostID INTEGER NOT NULL,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (UserID) REFERENCES members (MemberID),
            UNIQUE(UserID, PostType, PostID)
        )
    '''

    likes_postgres = '''
        CREATE TABLE IF NOT EXISTS likes (
            "LikeID" SERIAL PRIMARY KEY,
            "UserID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "PostType" TEXT NOT NULL,
            "PostID" INTEGER NOT NULL,
            "CreatedDate" DATE DEFAULT CURRENT_DATE,
            UNIQUE("UserID", "PostType", "PostID")
        )
    '''

    # user_favorites table
    user_favorites_sqlite = '''
        CREATE TABLE IF NOT EXISTS user_favorites (
            FavoriteID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            ItemType TEXT NOT NULL,
            ItemID INTEGER NOT NULL,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (UserID) REFERENCES members (MemberID),
            UNIQUE(UserID, ItemType, ItemID)
        )
    '''

    user_favorites_postgres = '''
        CREATE TABLE IF NOT EXISTS user_favorites (
            "FavoriteID" SERIAL PRIMARY KEY,
            "UserID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "ItemType" TEXT NOT NULL,
            "ItemID" INTEGER NOT NULL,
            "CreatedDate" DATE DEFAULT CURRENT_DATE,
            UNIQUE("UserID", "ItemType", "ItemID")
        )
    '''

    # follows table
    follows_sqlite = '''
        CREATE TABLE IF NOT EXISTS follows (
            FollowID INTEGER PRIMARY KEY AUTOINCREMENT,
            FollowerID INTEGER NOT NULL,
            FollowingID INTEGER NOT NULL,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (FollowerID) REFERENCES members (MemberID),
            FOREIGN KEY (FollowingID) REFERENCES members (MemberID),
            UNIQUE(FollowerID, FollowingID)
        )
    '''

    follows_postgres = '''
        CREATE TABLE IF NOT EXISTS follows (
            "FollowID" SERIAL PRIMARY KEY,
            "FollowerID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "FollowingID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "CreatedDate" DATE DEFAULT CURRENT_DATE,
            UNIQUE("FollowerID", "FollowingID")
        )
    '''

    # reports table
    reports_sqlite = '''
        CREATE TABLE IF NOT EXISTS reports (
            ReportID INTEGER PRIMARY KEY AUTOINCREMENT,
            ReporterID INTEGER NOT NULL,
            ReportedType TEXT NOT NULL,
            ReportedID INTEGER NOT NULL,
            Reason TEXT NOT NULL,
            Description TEXT,
            Status TEXT DEFAULT 'pending',
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (ReporterID) REFERENCES members (MemberID)
        )
    '''

    reports_postgres = '''
        CREATE TABLE IF NOT EXISTS reports (
            "ReportID" SERIAL PRIMARY KEY,
            "ReporterID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "ReportedType" TEXT NOT NULL,
            "ReportedID" INTEGER NOT NULL,
            "Reason" TEXT NOT NULL,
            "Description" TEXT,
            "Status" TEXT DEFAULT 'pending',
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # notifications table
    notifications_sqlite = '''
        CREATE TABLE IF NOT EXISTS notifications (
            NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Type TEXT NOT NULL,
            Title TEXT NOT NULL,
            Message TEXT NOT NULL,
            RelatedType TEXT,
            RelatedID INTEGER,
            IsRead INTEGER DEFAULT 0,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (UserID) REFERENCES members (MemberID)
        )
    '''

    notifications_postgres = '''
        CREATE TABLE IF NOT EXISTS notifications (
            "NotificationID" SERIAL PRIMARY KEY,
            "UserID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "Type" TEXT NOT NULL,
            "Title" TEXT NOT NULL,
            "Message" TEXT NOT NULL,
            "RelatedType" TEXT,
            "RelatedID" INTEGER,
            "IsRead" BOOLEAN DEFAULT FALSE,
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # user_activity_logs table
    user_activity_logs_sqlite = '''
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            LogID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            Action TEXT NOT NULL,
            Details TEXT,
            IPAddress TEXT,
            UserAgent TEXT,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (UserID) REFERENCES members (MemberID)
        )
    '''

    user_activity_logs_postgres = '''
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            "LogID" SERIAL PRIMARY KEY,
            "UserID" INTEGER REFERENCES members ("MemberID"),
            "Action" TEXT NOT NULL,
            "Details" TEXT,
            "IPAddress" TEXT,
            "UserAgent" TEXT,
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # promo_codes table
    promo_codes_sqlite = '''
        CREATE TABLE IF NOT EXISTS promo_codes (
            PromoCodeID INTEGER PRIMARY KEY AUTOINCREMENT,
            Code TEXT UNIQUE NOT NULL,
            DiscountType TEXT NOT NULL,
            DiscountValue REAL NOT NULL,
            UsageLimit INTEGER NOT NULL,
            UsedCount INTEGER DEFAULT 0,
            ExpirationDate DATE,
            Status TEXT DEFAULT 'active',
            CreatedBy INTEGER NOT NULL,
            CreatedDate DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (CreatedBy) REFERENCES members (MemberID)
        )
    '''

    promo_codes_postgres = '''
        CREATE TABLE IF NOT EXISTS promo_codes (
            "PromoCodeID" SERIAL PRIMARY KEY,
            "Code" TEXT UNIQUE NOT NULL,
            "DiscountType" TEXT NOT NULL,
            "DiscountValue" REAL NOT NULL,
            "UsageLimit" INTEGER NOT NULL,
            "UsedCount" INTEGER DEFAULT 0,
            "ExpirationDate" DATE,
            "Status" TEXT DEFAULT 'active',
            "CreatedBy" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # vehicle_comparisons table
    vehicle_comparisons_sqlite = '''
        CREATE TABLE IF NOT EXISTS vehicle_comparisons (
            ComparisonID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Vehicle1ID INTEGER NOT NULL,
            Vehicle2ID INTEGER NOT NULL,
            CreatedDate TEXT DEFAULT CURRENT_DATE,
            FOREIGN KEY (UserID) REFERENCES members (MemberID),
            FOREIGN KEY (Vehicle1ID) REFERENCES vehicles (id),
            FOREIGN KEY (Vehicle2ID) REFERENCES vehicles (id)
        )
    '''

    vehicle_comparisons_postgres = '''
        CREATE TABLE IF NOT EXISTS vehicle_comparisons (
            "ComparisonID" SERIAL PRIMARY KEY,
            "UserID" INTEGER NOT NULL REFERENCES members ("MemberID"),
            "Vehicle1ID" INTEGER NOT NULL REFERENCES vehicles (id),
            "Vehicle2ID" INTEGER NOT NULL REFERENCES vehicles (id),
            "CreatedDate" DATE DEFAULT CURRENT_DATE
        )
    '''

    # Execute table creation based on database type
    if db_manager.db_type == 'sqlite':
        tables = [
            ('vehicle_photos', vehicle_photos_sqlite),
            ('event_rsvps', event_rsvps_sqlite),
            ('blog_posts', blog_posts_sqlite),
            ('comments', comments_sqlite),
            ('likes', likes_sqlite),
            ('user_favorites', user_favorites_sqlite),
            ('follows', follows_sqlite),
            ('reports', reports_sqlite),
            ('notifications', notifications_sqlite),
            ('user_activity_logs', user_activity_logs_sqlite),
            ('promo_codes', promo_codes_sqlite),
            ('vehicle_comparisons', vehicle_comparisons_sqlite)
        ]
    else:
        tables = [
            ('vehicle_photos', vehicle_photos_postgres),
            ('event_rsvps', event_rsvps_postgres),
            ('blog_posts', blog_posts_postgres),
            ('comments', comments_postgres),
            ('likes', likes_postgres),
            ('user_favorites', user_favorites_postgres),
            ('follows', follows_postgres),
            ('reports', reports_postgres),
            ('notifications', notifications_postgres),
            ('user_activity_logs', user_activity_logs_postgres),
            ('promo_codes', promo_codes_postgres),
            ('vehicle_comparisons', vehicle_comparisons_postgres)
        ]

    with db_manager.get_db_connection() as conn:
        cursor = conn.cursor()
        for table_name, create_sql in tables:
            try:
                cursor.execute(create_sql)
                logger.info(f"Created table: {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
        conn.commit()

def add_columns_to_existing_tables():
    """Add new columns to existing tables"""

    # Add Featured column to vehicles table
    if db_manager.db_type == 'sqlite':
        alter_vehicles = "ALTER TABLE vehicles ADD COLUMN Featured INTEGER DEFAULT 0"
        alter_members = "ALTER TABLE members ADD COLUMN SocialLinks TEXT"
        alter_members_views = "ALTER TABLE vehicles ADD COLUMN Views INTEGER DEFAULT 0"
    else:
        alter_vehicles = 'ALTER TABLE vehicles ADD COLUMN "Featured" BOOLEAN DEFAULT FALSE'
        alter_members = 'ALTER TABLE members ADD COLUMN "SocialLinks" TEXT'
        alter_members_views = 'ALTER TABLE vehicles ADD COLUMN "Views" INTEGER DEFAULT 0'

    # Check and add columns
    columns_to_add = [
        ('vehicles', 'Featured', alter_vehicles),
        ('vehicles', 'Views', alter_members_views),
        ('members', 'SocialLinks', alter_members)
    ]

    with db_manager.get_db_connection() as conn:
        cursor = conn.cursor()
        for table, column, alter_sql in columns_to_add:
            try:
                # Check if column exists
                if db_manager.db_type == 'sqlite':
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]
                else:
                    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s", (table, column))
                    columns = cursor.fetchall()

                if column not in [col[0] if db_manager.db_type == 'postgres' else col for col in columns]:
                    cursor.execute(alter_sql)
                    logger.info(f"Added column {column} to table {table}")
                else:
                    logger.info(f"Column {column} already exists in table {table}")
            except Exception as e:
                logger.error(f"Error adding column {column} to {table}: {e}")
        conn.commit()

def run_migration():
    """Run the complete database migration"""
    logger.info("Starting database schema migration...")

    try:
        add_new_tables()
        add_columns_to_existing_tables()
        logger.info("Database schema migration completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()
