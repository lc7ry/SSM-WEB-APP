#!/usr/bin/env python3
"""
Test script to verify event creation works with the UCanAccess fix
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager_hybrid import db_manager

def test_event_creation():
    """Test creating an event with the fixed datetime handling"""

    print("🧪 Testing event creation with UCanAccess fix...")

    # Test data
    title = "Test Event - UCanAccess Fix"
    description = "This is a test event to verify the UCanAccess datetime fix works"
    location = "Test Location"
    event_date = "2024-01-20"
    event_time = "15:30:00"  # HH:MM:SS format
    max_attendees = 25
    place_id = 1  # Assuming place ID 1 exists

    # Create event_datetime by combining date and time
    event_datetime = f"{event_date} {event_time}"

    print(f"📅 Event DateTime: {event_datetime}")
    print(f"⏰ Event Time: {event_time}")

    try:
        # Insert test event
        insert_query = """
            INSERT INTO events (Title, Description, Location, EventDate, EventTime, MaxAttendees, CreatedBy, CreatedDate, PlaceID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        current_date = datetime.now().strftime('%Y-%m-%d')

        result = db_manager.execute_query(
            insert_query,
            [title, description, location, event_date, event_time, max_attendees, 1, current_date, place_id]
        )

        if result:
            print("✅ Event creation successful!")

            # Verify the event was created
            verify_query = "SELECT EventID, Title, EventDate FROM events WHERE Title = ?"
            events = db_manager.execute_query(verify_query, [title])

            if events:
                event = events[0]
                print(f"📋 Created event: ID={event[0]}, Title='{event[1]}', DateTime='{event[2]}'")
                print("✅ Event verification successful!")
                return True
            else:
                print("❌ Event creation failed - event not found after insertion")
                return False
        else:
            print("❌ Event creation failed - no result returned")
            return False

    except Exception as e:
        print(f"❌ Event creation failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_event_creation()
    if success:
        print("\n🎉 Test passed! The UCanAccess datetime fix is working correctly.")
    else:
        print("\n💥 Test failed! The fix needs more work.")
        sys.exit(1)
