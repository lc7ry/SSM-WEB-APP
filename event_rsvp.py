from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database_manager_hybrid import db_manager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

event_rsvp_bp = Blueprint('event_rsvp', __name__)

@event_rsvp_bp.route('/events')
def events_calendar():
    """Public events calendar with RSVP functionality"""
    try:
        # Get filter parameters
        category = request.args.get('category', 'all')
        location = request.args.get('location', '')
        upcoming_only = request.args.get('upcoming', 'true').lower() == 'true'

        # Build query for events
        query = """
        SELECT e.*, m.FirstName, m.LastName,
               COUNT(ea.AttendeeID) as attendee_count,
               p.Name as place_name, p.Address as place_address
        FROM events e
        LEFT JOIN members m ON e.CreatedBy = m.MemberID
        LEFT JOIN places p ON e.PlaceID = p.PlaceID
        LEFT JOIN event_attendees ea ON e.EventID = ea.EventID
        WHERE e.EventDate >= date('now')
        """

        params = []

        if category and category != 'all':
            query += " AND p.Type = ?"
            params.append(category)

        if location:
            query += " AND (e.Location LIKE ? OR p.Address LIKE ?)"
            search_param = f'%{location}%'
            params.extend([search_param, search_param])

        query += " GROUP BY e.EventID ORDER BY e.EventDate ASC, e.EventTime ASC"

        events = db_manager.execute_query(query, params)

        # Get unique event categories (place types)
        categories = db_manager.execute_query("SELECT DISTINCT Type FROM places WHERE Type IS NOT NULL ORDER BY Type")

        # Get upcoming events for featured section
        featured_events = db_manager.execute_query("""
            SELECT e.*, COUNT(ea.AttendeeID) as attendee_count
            FROM events e
            LEFT JOIN event_attendees ea ON e.EventID = ea.EventID
            WHERE e.EventDate >= date('now')
            GROUP BY e.EventID
            ORDER BY e.EventDate ASC
            LIMIT 3
        """)

        return render_template('events_calendar.html',
                             events=events,
                             categories=categories,
                             featured_events=featured_events,
                             category=category,
                             location=location,
                             upcoming_only=upcoming_only)

    except Exception as e:
        logger.error(f"Events calendar error: {e}")
        return render_template('events_calendar.html', error="Error loading events")

@event_rsvp_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    """Detailed view of a specific event"""
    try:
        # Get event details
        event = db_manager.execute_query("""
            SELECT e.*, m.FirstName, m.LastName, m.Username,
                   p.Name as place_name, p.Address as place_address,
                   p.Description as place_description
            FROM events e
            LEFT JOIN members m ON e.CreatedBy = m.MemberID
            LEFT JOIN places p ON e.PlaceID = p.PlaceID
            WHERE e.EventID = ?
        """, (event_id,))

        if not event:
            flash('Event not found', 'error')
            return redirect(url_for('event_rsvp.events_calendar'))

        event = event[0]

        # Get attendee count
        attendee_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM event_attendees WHERE EventID = ?",
            (event_id,)
        )[0][0]

        # Get RSVPs
        rsvps = db_manager.get_event_rsvps(event_id)

        # Get comments
        comments = db_manager.get_comments('event', event_id)

        # Get similar events
        similar_events = db_manager.execute_query("""
            SELECT e.*, COUNT(ea.AttendeeID) as attendee_count
            FROM events e
            LEFT JOIN event_attendees ea ON e.EventID = ea.EventID
            WHERE e.EventDate >= date('now') AND e.EventID != ?
            GROUP BY e.EventID
            ORDER BY e.EventDate ASC
            LIMIT 3
        """, (event_id,))

        # Compute creator name
        creator_name = f"{event[7]} {event[8]}" if event[7] and event[8] else (event[7] or event[8] or "Unknown")

        return render_template('event_detail.html',
                             event=event,
                             attendee_count=attendee_count,
                             rsvps=rsvps,
                             comments=comments,
                             similar_events=similar_events,
                             creator_name=creator_name)

    except Exception as e:
        logger.error(f"Event detail error: {e}")
        flash('Error loading event details', 'error')
        return redirect(url_for('event_rsvp.events_calendar'))

@event_rsvp_bp.route('/api/event/<int:event_id>/rsvp', methods=['POST'])
def submit_rsvp(event_id):
    """Submit RSVP for an event"""
    try:
        user_email = request.form.get('email')
        user_name = request.form.get('name')
        phone = request.form.get('phone')
        attendees = int(request.form.get('attendees', 1))
        notes = request.form.get('notes')

        if not user_email or not user_name:
            return jsonify({'success': False, 'error': 'Email and name are required'}), 400

        # Check if event exists and is upcoming
        event = db_manager.execute_query(
            "SELECT EventID, EventDate, MaxAttendees FROM events WHERE EventID = ? AND EventDate >= date('now')",
            (event_id,)
        )

        if not event:
            return jsonify({'success': False, 'error': 'Event not found or has passed'}), 404

        event = event[0]

        # Check capacity
        current_rsvps = db_manager.execute_query(
            "SELECT SUM(Attendees) FROM event_rsvps WHERE EventID = ?",
            (event_id,)
        )[0][0] or 0

        if event[2] and current_rsvps + attendees > event[2]:
            return jsonify({'success': False, 'error': 'Event is at capacity'}), 400

        # Submit RSVP
        db_manager.add_event_rsvp(event_id, user_email, user_name, phone, attendees, notes)

        return jsonify({
            'success': True,
            'message': f'RSVP submitted for {attendees} attendee(s)'
        })

    except Exception as e:
        logger.error(f"RSVP submission error: {e}")
        return jsonify({'success': False, 'error': 'Failed to submit RSVP'}), 500

@event_rsvp_bp.route('/api/event/<int:event_id>/comment', methods=['POST'])
def add_event_comment(event_id):
    """Add a comment to an event"""
    try:
        content = request.form.get('content')
        author_name = request.form.get('author_name')
        author_email = request.form.get('author_email')

        if not content or not content.strip():
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400

        if not author_name or not author_email:
            return jsonify({'success': False, 'error': 'Name and email are required'}), 400

        # For public comments, we'll create a temporary user ID or handle anonymously
        # For now, use a system user ID (this would need proper user management)
        system_user_id = 0  # Placeholder

        db_manager.add_comment(content.strip(), system_user_id, 'event', event_id, None)

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Add event comment error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add comment'}), 500

def init_app(app):
    """Initialize the event RSVP blueprint"""
    app.register_blueprint(event_rsvp_bp)
