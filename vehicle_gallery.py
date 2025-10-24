from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from database_manager_hybrid import db_manager
from permissions_manager import require_login
import logging

logger = logging.getLogger(__name__)

vehicle_gallery_bp = Blueprint('vehicle_gallery', __name__)

@vehicle_gallery_bp.route('/vehicle_gallery')
def vehicle_gallery():
    """Public vehicle gallery with filtering and search"""
    try:
        # Get filter parameters
        search = request.args.get('search', '')
        make_filter = request.args.get('make', '')
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        sort_by = request.args.get('sort', 'newest')  # newest, oldest, most_liked, most_viewed

        # Build query
        query = """
        SELECT v.*, m.FirstName, m.LastName,
               COUNT(DISTINCT vp.PhotoID) as photo_count,
               COUNT(DISTINCT l.LikeID) as like_count
        FROM vehicles v
        LEFT JOIN members m ON v.OwnerID = m.MemberID
        LEFT JOIN vehicle_photos vp ON v.id = vp.VehicleID
        LEFT JOIN likes l ON v.id = l.PostID AND l.PostType = 'vehicle'
        WHERE 1=1
        """

        params = []

        # Add search filter
        if search:
            query += " AND (v.Make LIKE ? OR v.Model LIKE ? OR v.Year LIKE ?)"
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])

        # Add make filter
        if make_filter and make_filter != 'all':
            query += " AND v.Make = ?"
            params.append(make_filter)

        # Add featured filter
        if featured_only:
            query += " AND v.Featured = 1"

        # Group by and add sorting
        query += " GROUP BY v.id"

        if sort_by == 'newest':
            query += " ORDER BY v.id DESC"
        elif sort_by == 'oldest':
            query += " ORDER BY v.id ASC"
        elif sort_by == 'most_liked':
            query += " ORDER BY like_count DESC"
        elif sort_by == 'most_viewed':
            query += " ORDER BY v.Views DESC"

        vehicles = db_manager.execute_query(query, params)

        # Get unique makes for filter dropdown
        makes = db_manager.execute_query("SELECT DISTINCT Make FROM vehicles WHERE Make IS NOT NULL ORDER BY Make")

        # Get featured vehicles for showcase
        featured_vehicles = db_manager.execute_query("""
            SELECT v.*, COUNT(vp.PhotoID) as photo_count
            FROM vehicles v
            LEFT JOIN vehicle_photos vp ON v.id = vp.VehicleID
            WHERE v.Featured = 1
            GROUP BY v.id
            ORDER BY v.id DESC
            LIMIT 6
        """)

        return render_template('vehicle_gallery.html',
                             vehicles=vehicles,
                             makes=makes,
                             featured_vehicles=featured_vehicles,
                             search=search,
                             make_filter=make_filter,
                             featured_only=featured_only,
                             sort_by=sort_by)

    except Exception as e:
        logger.error(f"Vehicle gallery error: {e}")
        return render_template('vehicle_gallery.html', error="Error loading vehicle gallery")

@vehicle_gallery_bp.route('/vehicle/<int:vehicle_id>')
def vehicle_detail(vehicle_id):
    """Detailed view of a specific vehicle"""
    try:
        # Get vehicle details
        vehicle = db_manager.execute_query("""
            SELECT v.*, m.FirstName, m.LastName, m.Username
            FROM vehicles v
            LEFT JOIN members m ON v.OwnerID = m.MemberID
            WHERE v.id = ?
        """, (vehicle_id,))

        if not vehicle:
            flash('Vehicle not found', 'error')
            return redirect(url_for('vehicle_gallery.vehicle_gallery'))

        vehicle = vehicle[0]

        # Get vehicle photos
        photos = db_manager.get_vehicle_photos(vehicle_id)

        # Get comments
        comments = db_manager.get_comments('vehicle', vehicle_id)

        # Increment view count
        db_manager.execute_query("UPDATE vehicles SET Views = Views + 1 WHERE id = ?", (vehicle_id,))

        # Get like count
        like_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM likes WHERE PostType = 'vehicle' AND PostID = ?",
            (vehicle_id,)
        )[0][0]

        # Check if current user liked this vehicle
        user_liked = False
        if hasattr(request, 'current_user') and request.current_user:
            user_like = db_manager.execute_query(
                "SELECT LikeID FROM likes WHERE UserID = ? AND PostType = 'vehicle' AND PostID = ?",
                (request.current_user.id, vehicle_id)
            )
            user_liked = len(user_like) > 0

        # Get similar vehicles
        similar_vehicles = db_manager.execute_query("""
            SELECT v.*, COUNT(vp.PhotoID) as photo_count
            FROM vehicles v
            LEFT JOIN vehicle_photos vp ON v.id = vp.VehicleID
            WHERE v.Make = ? AND v.id != ?
            GROUP BY v.id
            ORDER BY v.id DESC
            LIMIT 4
        """, (vehicle[2], vehicle_id))  # vehicle[2] is Make

        return render_template('vehicle_detail.html',
                             vehicle=vehicle,
                             photos=photos,
                             comments=comments,
                             like_count=like_count,
                             user_liked=user_liked,
                             similar_vehicles=similar_vehicles)

    except Exception as e:
        logger.error(f"Vehicle detail error: {e}")
        flash('Error loading vehicle details', 'error')
        return redirect(url_for('vehicle_gallery.vehicle_gallery'))

@vehicle_gallery_bp.route('/api/vehicle/<int:vehicle_id>/like', methods=['POST'])
@require_login
def toggle_vehicle_like(vehicle_id):
    """Toggle like on a vehicle"""
    try:
        user_id = request.current_user.id
        liked = db_manager.toggle_like(user_id, 'vehicle', vehicle_id)

        # Get updated like count
        like_count = db_manager.execute_query(
            "SELECT COUNT(*) FROM likes WHERE PostType = 'vehicle' AND PostID = ?",
            (vehicle_id,)
        )[0][0]

        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })

    except Exception as e:
        logger.error(f"Toggle like error: {e}")
        return jsonify({'success': False, 'error': 'Failed to toggle like'}), 500

@vehicle_gallery_bp.route('/api/vehicle/<int:vehicle_id>/comment', methods=['POST'])
@require_login
def add_vehicle_comment(vehicle_id):
    """Add a comment to a vehicle"""
    try:
        content = request.form.get('content')
        if not content or not content.strip():
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400

        user_id = request.current_user.id
        parent_comment_id = request.form.get('parent_comment_id')

        db_manager.add_comment(content.strip(), user_id, 'vehicle', vehicle_id, parent_comment_id)

        # Log activity
        db_manager.log_activity(user_id, 'comment_added', f'Commented on vehicle {vehicle_id}')

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Add comment error: {e}")
        return jsonify({'success': False, 'error': 'Failed to add comment'}), 500

@vehicle_gallery_bp.route('/api/vehicle/<int:vehicle_id>/favorite', methods=['POST'])
@require_login
def toggle_vehicle_favorite(vehicle_id):
    """Toggle favorite status for a vehicle"""
    try:
        user_id = request.current_user.id
        favorited = db_manager.toggle_favorite(user_id, 'vehicle', vehicle_id)

        return jsonify({
            'success': True,
            'favorited': favorited
        })

    except Exception as e:
        logger.error(f"Toggle favorite error: {e}")
        return jsonify({'success': False, 'error': 'Failed to toggle favorite'}), 500

def init_app(app):
    """Initialize the vehicle gallery blueprint"""
    app.register_blueprint(vehicle_gallery_bp)
