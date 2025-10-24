import sqlite3
import os

def migrate_database():
    """Migrate the database to add new tables and columns for enhanced features"""

    db_path = 'carmeet_community.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Starting database migration...")

    # Create new tables for enhanced features
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS vehicle_photos (
            PhotoID INTEGER PRIMARY KEY AUTOINCREMENT,
            VehicleID INTEGER NOT NULL,
            PhotoURL TEXT NOT NULL,
            Caption TEXT,
            IsPrimary BOOLEAN DEFAULT 0,
            UploadDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (VehicleID) REFERENCES vehicles(id)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS event_rsvps (
            RSVP_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EventID INTEGER NOT NULL,
            UserEmail TEXT NOT NULL,
            UserName TEXT,
            Phone TEXT,
            Attendees INTEGER DEFAULT 1,
            RSVPDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            Status TEXT DEFAULT 'confirmed',
            Notes TEXT,
            FOREIGN KEY (EventID) REFERENCES events(EventID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS blog_posts (
            PostID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Content TEXT NOT NULL,
            AuthorID INTEGER NOT NULL,
            Category TEXT,
            Tags TEXT,
            Featured BOOLEAN DEFAULT 0,
            Published BOOLEAN DEFAULT 1,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            UpdatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            Views INTEGER DEFAULT 0,
            Likes INTEGER DEFAULT 0,
            FOREIGN KEY (AuthorID) REFERENCES members(MemberID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS comments (
            CommentID INTEGER PRIMARY KEY AUTOINCREMENT,
            Content TEXT NOT NULL,
            AuthorID INTEGER NOT NULL,
            PostType TEXT NOT NULL,
            PostID INTEGER NOT NULL,
            ParentCommentID INTEGER,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            Likes INTEGER DEFAULT 0,
            FOREIGN KEY (AuthorID) REFERENCES members(MemberID),
            FOREIGN KEY (ParentCommentID) REFERENCES comments(CommentID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS likes (
            LikeID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            PostType TEXT NOT NULL,
            PostID INTEGER NOT NULL,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES members(MemberID),
            UNIQUE(UserID, PostType, PostID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS user_favorites (
            FavoriteID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            ItemType TEXT NOT NULL,
            ItemID INTEGER NOT NULL,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES members(MemberID),
            UNIQUE(UserID, ItemType, ItemID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS follows (
            FollowID INTEGER PRIMARY KEY AUTOINCREMENT,
            FollowerID INTEGER NOT NULL,
            FollowingID INTEGER NOT NULL,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (FollowerID) REFERENCES members(MemberID),
            FOREIGN KEY (FollowingID) REFERENCES members(MemberID),
            UNIQUE(FollowerID, FollowingID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS reports (
            ReportID INTEGER PRIMARY KEY AUTOINCREMENT,
            ReporterID INTEGER NOT NULL,
            ReportedType TEXT NOT NULL,
            ReportedID INTEGER NOT NULL,
            Reason TEXT NOT NULL,
            Description TEXT,
            Status TEXT DEFAULT 'pending',
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            ReviewedDate DATETIME,
            ReviewedBy INTEGER,
            FOREIGN KEY (ReporterID) REFERENCES members(MemberID),
            FOREIGN KEY (ReviewedBy) REFERENCES members(MemberID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS notifications (
            NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Type TEXT NOT NULL,
            Title TEXT NOT NULL,
            Message TEXT NOT NULL,
            RelatedType TEXT,
            RelatedID INTEGER,
            IsRead BOOLEAN DEFAULT 0,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES members(MemberID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            LogID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER,
            Action TEXT NOT NULL,
            Details TEXT,
            IPAddress TEXT,
            UserAgent TEXT,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES members(MemberID)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS vehicle_comparisons (
            ComparisonID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID INTEGER NOT NULL,
            Vehicle1ID INTEGER NOT NULL,
            Vehicle2ID INTEGER NOT NULL,
            CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserID) REFERENCES members(MemberID),
            FOREIGN KEY (Vehicle1ID) REFERENCES vehicles(id),
            FOREIGN KEY (Vehicle2ID) REFERENCES vehicles(id)
        )
        '''
    ]

    # Execute table creation
    for i, table_sql in enumerate(tables, 1):
        try:
            cursor.execute(table_sql)
            print(f"✓ Created table {i}/11 successfully")
        except Exception as e:
            print(f"✗ Error creating table {i}: {e}")

    # Add new columns to existing tables
    alter_statements = [
        ('members', 'SocialLinks', 'TEXT'),
        ('members', 'Bio', 'TEXT'),
        ('members', 'Location', 'TEXT'),
        ('members', 'ProfilePicture', 'TEXT'),
        ('members', 'LastLogin', 'DATETIME'),
        ('vehicles', 'Featured', 'BOOLEAN DEFAULT 0'),
        ('vehicles', 'Views', 'INTEGER DEFAULT 0'),
        ('vehicles', 'Likes', 'INTEGER DEFAULT 0'),
        ('events', 'Featured', 'BOOLEAN DEFAULT 0'),
        ('events', 'Views', 'INTEGER DEFAULT 0'),
        ('events', 'RSVPs', 'INTEGER DEFAULT 0'),
        ('places', 'Featured', 'BOOLEAN DEFAULT 0'),
        ('places', 'Rating', 'REAL DEFAULT 0'),
        ('places', 'ReviewCount', 'INTEGER DEFAULT 0')
    ]

    for table, column, column_type in alter_statements:
        try:
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {column_type}')
            print(f"✓ Added {column} to {table}")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f"⚠ {column} already exists in {table}, skipping")
            else:
                print(f"✗ Error adding {column} to {table}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error adding {column} to {table}: {e}")

    # Commit changes and close
    conn.commit()
    conn.close()

    print("\n✅ Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
