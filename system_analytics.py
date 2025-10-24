from flask import Blueprint, render_template, jsonify
from database_manager_hybrid import db_manager
from permissions_manager import require_admin
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

system_analytics_bp = Blueprint('system_analytics', __name__)

@system_analytics_bp.route('/system_analytics')
@require_admin
def system_analytics():
    """Display system analytics dashboard"""
    try:
        # Get user activity statistics
        total_users = db_manager.execute_query("SELECT COUNT(*) FROM members")[0][0]
        # Note: LastLogin column doesn't exist in members table, so we'll use JoinDate as proxy for active users
        active_users = db_manager.execute_query("SELECT COUNT(*) FROM members WHERE JoinDate >= date('now', '-30 days')")[0][0] if db_manager.db_type == 'sqlite' else db_manager.execute_query("SELECT COUNT(*) FROM members WHERE JoinDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)")[0][0]

        # Get event statistics
        total_events = db_manager.execute_query("SELECT COUNT(*) FROM events")[0][0]
        upcoming_events = db_manager.execute_query("SELECT COUNT(*) FROM events WHERE EventDate >= date('now')")[0][0] if db_manager.db_type == 'sqlite' else db_manager.execute_query("SELECT COUNT(*) FROM events WHERE EventDate >= CURDATE()")[0][0]
        past_events = total_events - upcoming_events

        # Get vehicle statistics
        total_vehicles = db_manager.execute_query("SELECT COUNT(*) FROM vehicles")[0][0]

        # Get ticket statistics if tickets table exists
        ticket_stats = {'total': 0, 'sold': 0, 'revenue': 0}
        if db_manager.table_exists('tickets'):
            ticket_stats['total'] = db_manager.execute_query("SELECT COUNT(*) FROM tickets")[0][0]
            ticket_stats['sold'] = db_manager.execute_query("SELECT COUNT(*) FROM tickets WHERE Status IN ('valid', 'used')")[0][0]
            revenue_result = db_manager.execute_query("SELECT SUM(Price) FROM tickets WHERE Status IN ('valid', 'used')")[0][0]
            ticket_stats['revenue'] = revenue_result if revenue_result else 0

        # Get recent activity (last 10 actions)
        recent_activity = []
        try:
            # Get recent member registrations
            new_members = db_manager.execute_query("""
                SELECT Username, JoinDate FROM members
                ORDER BY JoinDate DESC LIMIT 3
            """)
            for member in new_members:
                recent_activity.append({
                    'type': 'user_registration',
                    'description': f"New member: {member[0]}",
                    'timestamp': member[1],
                    'icon': 'fas fa-user-plus',
                    'color': 'success'
                })

            # Get recent events
            recent_events = db_manager.execute_query("""
                SELECT Title, CreatedDate FROM events
                ORDER BY CreatedDate DESC LIMIT 3
            """)
            for event in recent_events:
                recent_activity.append({
                    'type': 'event_created',
                    'description': f"Event created: {event[0]}",
                    'timestamp': event[1],
                    'icon': 'fas fa-calendar-plus',
                    'color': 'info'
                })

            # Sort by timestamp and limit to 10
            recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_activity = recent_activity[:10]

        except Exception as e:
            logger.error(f"Error fetching recent activity: {e}")

        # Get system health metrics
        system_health = {
            'database_status': 'healthy',
            'last_backup': 'Unknown',
            'server_uptime': 'Unknown',
            'memory_usage': 'Unknown'
        }

        return render_template('system_analytics.html',
                             total_users=total_users,
                             active_users=active_users,
                             total_events=total_events,
                             upcoming_events=upcoming_events,
                             past_events=past_events,
                             total_vehicles=total_vehicles,
                             ticket_stats=ticket_stats,
                             recent_activity=recent_activity,
                             system_health=system_health)

    except Exception as e:
        logger.error(f"System analytics error: {e}")
        return render_template('system_analytics.html',
                             error="Error loading analytics data")

@system_analytics_bp.route('/api/analytics/user_growth')
@require_admin
def user_growth_api():
    """API endpoint for user growth chart data"""
    try:
        # Get user registration data for the last 12 months
        if db_manager.db_type == 'sqlite':
            growth_data = db_manager.execute_query("""
                SELECT strftime('%Y-%m', JoinDate) as month, COUNT(*) as count
                FROM members
                WHERE JoinDate >= date('now', '-12 months')
                GROUP BY strftime('%Y-%m', JoinDate)
                ORDER BY month
            """)
        else:
            growth_data = db_manager.execute_query("""
                SELECT DATE_FORMAT(JoinDate, '%Y-%m') as month, COUNT(*) as count
                FROM members
                WHERE JoinDate >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(JoinDate, '%Y-%m')
                ORDER BY month
            """)

        data = {
            'labels': [row[0] for row in growth_data],
            'data': [row[1] for row in growth_data]
        }

        return jsonify(data)

    except Exception as e:
        logger.error(f"User growth API error: {e}")
        return jsonify({'error': 'Failed to fetch user growth data'}), 500

@system_analytics_bp.route('/api/analytics/event_participation')
@require_admin
def event_participation_api():
    """API endpoint for event participation chart data"""
    try:
        # Get event participation data
        participation_data = db_manager.execute_query("""
            SELECT e.Title, COUNT(ea.AttendeeID) as attendees
            FROM events e
            LEFT JOIN event_attendees ea ON e.EventID = ea.EventID
            WHERE e.EventDate >= date('now', '-6 months')
            GROUP BY e.EventID, e.Title
            ORDER BY attendees DESC
            LIMIT 10
        """) if db_manager.db_type == 'sqlite' else db_manager.execute_query("""
            SELECT e.Title, COUNT(ea.AttendeeID) as attendees
            FROM events e
            LEFT JOIN event_attendees ea ON e.EventID = ea.EventID
            WHERE e.EventDate >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY e.EventID, e.Title
            ORDER BY attendees DESC
            LIMIT 10
        """)

        data = {
            'labels': [row[0] for row in participation_data],
            'data': [row[1] for row in participation_data]
        }

        return jsonify(data)

    except Exception as e:
        logger.error(f"Event participation API error: {e}")
        return jsonify({'error': 'Failed to fetch event participation data'}), 500

def init_app(app):
    """Initialize the system analytics blueprint"""
    app.register_blueprint(system_analytics_bp)
