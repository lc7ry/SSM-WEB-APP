import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import subprocess
import threading
import time
import secrets
from datetime import datetime, timedelta
from database_manager_hybrid import db_manager
from permissions_manager import PermissionManager, require_permission, require_admin, get_user_role
from ticket_system import init_app as init_ticket_app
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize ticket system
init_ticket_app(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['DEBUG'] = False
    # Production logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['DEBUG'] = True
    # Development logging
    logging.basicConfig(filename='app.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Context processor to make user available in templates
@app.context_processor
def inject_user():
    def get_current_user():
        if 'user_id' in session:
            try:
                user = db_manager.execute_query(
                    "SELECT * FROM members WHERE MemberID = ?",
                    [session['user_id']]
                )
                if user:
                    user_data = user[0]
                    permissions = PermissionManager.get_user_permissions(session['user_id'])
                    role = get_user_role(session['user_id'])
                    return {
                        'id': user_data[0],
                        'username': user_data[1],
                        'email': user_data[3],
                        'first_name': user_data[4],
                        'last_name': user_data[5],
                        'role': role,
                        'permissions': permissions
                    }
                return None
            except Exception as e:
                logger.error(f"Error getting current user: {e}")
                return None
        return None
    
    return dict(current_user=get_current_user())



# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking login for {request.endpoint}, user_id in session: {'user_id' in session}")
        if 'user_id' not in session:
            # Prevent redirect loop by checking if we're already on login page
            if request.endpoint and request.endpoint == 'login':
                return f(*args, **kwargs)
            # Also check the path to be safe with tunnels
            if request.path in ['/login', '/register', '/']:
                return f(*args, **kwargs)
            logger.info(f"Redirecting to login from {request.endpoint}")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    logger.info("Handling request for index")
    # Redirect logged in users to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        try:
            user = db_manager.execute_query(
                "SELECT * FROM members WHERE Username = ?",
                [username]
            )
            
            if user and check_password_hash(user[0][2], password):
                session['user_id'] = user[0][0]
                session['username'] = user[0][1]
                flash('Login successful!', 'success')
                # Check if there's a next URL parameter
                next_url = request.args.get('next')
                if next_url and next_url != url_for('login') and next_url != url_for('logout'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        
        try:
            # Validate input
            if not all([username, email, password, first_name, last_name]):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
                return redirect(url_for('register'))
            
            # Use database manager for registration
            result = db_manager.register_user(username, email, password, first_name, last_name)
            
            if result['success']:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash(result['error'], 'error')
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        user_role = get_user_role(session['user_id'])

        if user_role == 'member':
            # Member dashboard - show only events and places
            events = db_manager.execute_query("SELECT * FROM events ORDER BY EventDate DESC LIMIT 5")
            places = db_manager.execute_query("SELECT * FROM places ORDER BY Name LIMIT 5")
            return render_template('index_member.html', events=events, places=places)

        # Admin/Moderator dashboard - show full dashboard
        total_members = db_manager.execute_query("SELECT COUNT(*) FROM members")[0][0]
        total_vehicles = db_manager.execute_query("SELECT COUNT(*) FROM vehicles")[0][0]
        upcoming_events = db_manager.execute_query("SELECT COUNT(*) FROM events WHERE EventDate >= DATE()")[0][0]

        # Get ticket statistics for admin dashboard
        total_tickets = db_manager.execute_query("SELECT COUNT(*) FROM tickets")[0][0] if db_manager.table_exists('tickets') else 0
        valid_tickets = db_manager.execute_query("SELECT COUNT(*) FROM tickets WHERE Status = 'valid'")[0][0] if db_manager.table_exists('tickets') else 0
        used_tickets = db_manager.execute_query("SELECT COUNT(*) FROM tickets WHERE Status = 'used'")[0][0] if db_manager.table_exists('tickets') else 0

        # Calculate total revenue
        revenue_result = db_manager.execute_query("SELECT SUM(Price) FROM tickets WHERE Status IN ('valid', 'used')")[0][0] if db_manager.table_exists('tickets') else 0
        total_revenue = revenue_result if revenue_result else 0

        return render_template('dashboard.html',
                           total_members=total_members,
                           total_vehicles=total_vehicles,
                           upcoming_events=upcoming_events,
                           total_tickets=total_tickets,
                           valid_tickets=valid_tickets,
                           used_tickets=used_tickets,
                           total_revenue=total_revenue)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html',
                           total_members=0,
                           total_vehicles=0,
                           upcoming_events=0,
                           total_tickets=0,
                           valid_tickets=0,
                           used_tickets=0,
                           total_revenue=0)

@app.route('/members')
@require_admin
def members():
    try:
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'Username')
        
        query = "SELECT * FROM members"
        params = []
        
        if search:
            query += " WHERE Username LIKE ? OR FirstName LIKE ? OR LastName LIKE ?"
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if sort_by == 'Username':
            query += " ORDER BY Username"
        elif sort_by == 'JoinDate':
            query += " ORDER BY JoinDate DESC"
        
        members = db_manager.execute_query(query, params)
        
        return render_template('members.html', members=members, search=search, sort_by=sort_by)
    except Exception as e:
        logger.error(f"Members error: {e}")
        return render_template('members.html', members=[], search='', sort_by='Username')

@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@require_admin
def edit_member(member_id):
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            phone = request.form.get('phone', '').strip()
            bio = request.form.get('bio', '').strip()
            profile_picture = request.form.get('profile_picture', '').strip()
            location = request.form.get('location', '').strip()

            # Handle file upload
            if 'profile_picture_file' in request.files:
                file = request.files['profile_picture_file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    profile_picture = f'/static/uploads/{filename}'

            # Validate required fields
            if not all([username, email, first_name, last_name]):
                flash('Username, email, first name, and last name are required', 'error')
                return redirect(url_for('edit_member', member_id=member_id))

            # Update member in the database
            update_query = """
                UPDATE members
                SET Username = ?, Email = ?, FirstName = ?, LastName = ?, Phone = ?, Bio = ?, ProfilePicture = ?, Location = ?
                WHERE MemberID = ?
            """

            result = db_manager.execute_query(
                update_query,
                [username, email, first_name, last_name, phone, bio, profile_picture, location, member_id]
            )

            if result > 0:
                flash('Member updated successfully!', 'success')
                return redirect(url_for('members'))
            else:
                flash('Failed to update member. Please try again.', 'error')
                return redirect(url_for('edit_member', member_id=member_id))

        except Exception as e:
            logger.error(f"Edit member error: {e}")
            flash('Error updating member. Please try again.', 'error')
            return redirect(url_for('edit_member', member_id=member_id))

    # GET request - fetch member details to pre-fill the form
    member = db_manager.execute_query("SELECT * FROM members WHERE MemberID = ?", [member_id])
    if member:
        return render_template('edit_member.html', member=member[0])
    else:
        flash('Member not found', 'error')
        return redirect(url_for('members'))

@app.route('/vehicles')
@login_required
def vehicles():
    try:
        search = request.args.get('search', '')
        make_filter = request.args.get('make', '')
        
        query = """
            SELECT v.*, m.FirstName, m.LastName 
            FROM vehicles v 
            JOIN members m ON v.MemberID = m.MemberID
        """
        params = []
        
        if search:
            query += " WHERE v.Make LIKE ? OR v.Model LIKE ? OR m.FirstName LIKE ? OR m.LastName LIKE ?"
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param, search_param])
        
        if make_filter:
            if search:
                query += " AND v.Make = ?"
            else:
                query += " WHERE v.Make = ?"
            params.append(make_filter)
        
        vehicles = db_manager.execute_query(query, params)
        
        return render_template('vehicles.html', vehicles=vehicles, search=search, make_filter=make_filter)
    except Exception as e:
        logger.error(f"Vehicles error: {e}")
        return render_template('vehicles.html', vehicles=[], search='', make_filter='')

@app.route('/vehicle_detail/<int:vehicle_id>')
@login_required
def vehicle_detail(vehicle_id):
    try:
        vehicle = db_manager.execute_query("SELECT * FROM vehicles WHERE id = ?", [vehicle_id])
        if vehicle:
            return render_template('vehicle_detail.html', vehicle=vehicle[0])
        else:
            flash('Vehicle not found', 'error')
            return redirect(url_for('vehicles'))
    except Exception as e:
        logger.error(f"Vehicle detail error for vehicle ID {vehicle_id}: {e}")
        flash('Error retrieving vehicle details', 'error')
        return redirect(url_for('vehicles'))

@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@require_permission('manage_vehicles')
def edit_vehicle(vehicle_id):
    if request.method == 'POST':
        # Handle the form submission for editing the vehicle
        make = request.form.get('make', '').strip()
        model = request.form.get('model', '').strip()
        year_str = request.form.get('year', '').strip()
        color = request.form.get('color', '').strip()
        license_plate = request.form.get('license_plate', '').strip().upper()
        description = request.form.get('description', '').strip()
        
        # Validate required fields
        if not make or not model or not year_str or not color or not license_plate:
            flash('All fields are required', 'error')
            return redirect(url_for('edit_vehicle', vehicle_id=vehicle_id))
        
        try:
            year = int(year_str)
            if year < 1900 or year > 2030:
                flash('Please enter a valid year between 1900 and 2030', 'error')
                return redirect(url_for('edit_vehicle', vehicle_id=vehicle_id))
        except ValueError:
            flash('Please enter a valid year', 'error')
            return redirect(url_for('edit_vehicle', vehicle_id=vehicle_id))
        
        # Update vehicle in the database
        update_query = """
            UPDATE vehicles 
            SET Make = ?, Model = ?, Year = ?, Color = ?, LicensePlate = ?, Description = ?
            WHERE id = ?
        """
        
        result = db_manager.execute_query(
            update_query,
            [make, model, year, color, license_plate, description, vehicle_id]
        )
        
        if result > 0:
            flash('Vehicle updated successfully!', 'success')
            return redirect(url_for('vehicles'))
        else:
            flash('Failed to update vehicle. Please try again.', 'error')
            return redirect(url_for('edit_vehicle', vehicle_id=vehicle_id))
    
    # Fetch the vehicle details to pre-fill the form
    vehicle = db_manager.execute_query("SELECT * FROM vehicles WHERE id = ?", [vehicle_id])
    if vehicle:
        return render_template('edit_vehicle.html', vehicle=vehicle[0])
    else:
        flash('Vehicle not found', 'error')
        return redirect(url_for('vehicles'))

@app.route('/places')
def places():
    try:
        places = db_manager.execute_query("SELECT * FROM places")
        return render_template('places.html', places=places)
    except Exception as e:
        logger.error(f"Places error: {e}")
    return render_template('places.html', places=[])

@app.route('/events')
def events():
    try:
        search = request.args.get('search', '')
        filter_type = request.args.get('filter', '')

        query = "SELECT * FROM events"
        params = []

        if search:
            query += " WHERE Title LIKE ? OR Description LIKE ? OR Location LIKE ?"
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])

        if filter_type == 'upcoming':
            if search:
                query += " AND EventDate >= DATE()"
            else:
                query += " WHERE EventDate >= DATE()"
        elif filter_type == 'past':
            if search:
                query += " AND EventDate < DATE()"
            else:
                query += " WHERE EventDate < DATE()"

        query += " ORDER BY EventDate DESC"
        events = db_manager.execute_query(query, params)

        # Calculate stats
        upcoming_events_count = len([e for e in events if e[2] >= str(datetime.now().date())]) if events else 0
        past_events_count = len([e for e in events if e[2] < str(datetime.now().date())]) if events else 0

        return render_template('events.html',
                             events=events,
                             search=search,
                             filter=filter_type,
                             upcoming_events_count=upcoming_events_count,
                             past_events_count=past_events_count)
    except Exception as e:
        logger.error(f"Events error: {e}")
    return render_template('events.html', events=[], search='', filter='', upcoming_events_count=0, past_events_count=0)

@app.route('/event_detail/<int:event_id>')
def event_detail(event_id):
    try:
        event = db_manager.execute_query("SELECT * FROM events WHERE EventID = ?", [event_id])
        if event:
            # Get attendee count
            attendee_count = db_manager.execute_query(
                "SELECT COUNT(*) FROM event_attendees WHERE EventID = ?",
                [event_id]
            )[0][0]

            # Get creator info
            creator = db_manager.execute_query(
                "SELECT FirstName, LastName FROM members WHERE MemberID = ?",
                [event[0][6]]  # CreatedBy field
            )

            creator_name = f"{creator[0][0]} {creator[0][1]}" if creator else "Unknown"

            return render_template('event_detail.html',
                                 event=event[0],
                                 attendee_count=attendee_count,
                                 creator_name=creator_name)
        else:
            flash('Event not found', 'error')
            return redirect(url_for('events'))
    except Exception as e:
        logger.error(f"Event detail error for event ID {event_id}: {e}")
        flash('Error retrieving event details', 'error')
        return redirect(url_for('events'))

@app.route('/add_vehicle', methods=['GET', 'POST'])
@require_permission('manage_vehicles')
def add_vehicle():
    """Handle vehicle registration"""
    if request.method == 'POST':
        try:
            # Get form data with better validation
            make = request.form.get('make', '').strip()
            model = request.form.get('model', '').strip()
            year_str = request.form.get('year', '').strip()
            color = request.form.get('color', '').strip()
            license_plate = request.form.get('license_plate', '').strip().upper()
            description = request.form.get('description', '').strip()
            
            # Validate required fields
            if not make:
                flash('Please select a vehicle make', 'error')
                return render_template('add_vehicle.html')
            if not model:
                flash('Please enter a vehicle model', 'error')
                return render_template('add_vehicle.html')
            if not year_str:
                flash('Please enter a vehicle year', 'error')
                return render_template('add_vehicle.html')
            
            try:
                year = int(year_str)
                if year < 1900 or year > 2030:
                    flash('Please enter a valid year between 1900 and 2030', 'error')
                    return render_template('add_vehicle.html')
            except ValueError:
                flash('Please enter a valid year', 'error')
                return render_template('add_vehicle.html')
            
            if not color:
                flash('Please enter a vehicle color', 'error')
                return render_template('add_vehicle.html')
            if not license_plate:
                flash('Please enter a license plate', 'error')
                return render_template('add_vehicle.html')
            
            # Check if license plate already exists
            existing = db_manager.execute_query(
                "SELECT * FROM vehicles WHERE LicensePlate = ?",
                [license_plate]
            )
            
            if existing:
                flash(f'A vehicle with license plate "{license_plate}" already exists', 'error')
                return render_template('add_vehicle.html')
            
            # Insert new vehicle
            insert_query = """
                INSERT INTO vehicles (MemberID, Make, Model, Year, Color, LicensePlate, Description, DateAdded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            result = db_manager.execute_query(
                insert_query,
                [session['user_id'], make, model, year, color, license_plate, description, current_date]
            )
            
            if result > 0:
                flash(f'Vehicle "{make} {model}" registered successfully! You can add another vehicle below.', 'success')
                # Clear form data by redirecting back to add_vehicle
                return redirect(url_for('add_vehicle'))
            else:
                flash('Failed to register vehicle. Please try again.', 'error')
                
        except Exception as e:
            logger.error(f"Add vehicle error: {e}")
            flash(f'Error registering vehicle: {str(e)}', 'error')
    
    return render_template('add_vehicle.html')

@app.route('/add_event', methods=['GET', 'POST'])
@require_permission('post_events')
def add_event():
    """Handle event creation"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            place_id = request.form.get('place_id')
            event_date = request.form.get('event_date')
            event_time = request.form.get('event_time')
            max_attendees_str = request.form.get('max_attendees', '50').strip()

            # Validate required fields
            if not all([title, description, place_id, event_date, event_time]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('add_event'))

            # Validate and convert max_attendees
            try:
                max_attendees = int(max_attendees_str)
                if max_attendees < 1:
                    max_attendees = 50
            except (ValueError, TypeError):
                max_attendees = 50

            # Get place details for location
            try:
                place = db_manager.execute_query("SELECT Name, Address FROM places WHERE PlaceID = ?", [place_id])
                if not place:
                    flash('Selected place not found', 'error')
                    return redirect(url_for('add_event'))

                location = f"{place[0][0]} - {place[0][1]}"
            except Exception as e:
                logger.error(f"Error fetching place details: {e}")
                flash('Error retrieving place information', 'error')
                return redirect(url_for('add_event'))

            # Insert new event
            insert_query = """
                INSERT INTO events (Title, Description, Location, EventDate, EventTime, MaxAttendees, CreatedBy, CreatedDate, PlaceID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            current_date = datetime.now().strftime('%Y-%m-%d')

            result = db_manager.execute_query(
                insert_query,
                [title, description, location, event_date, event_time, max_attendees, session['user_id'], current_date, place_id]
            )

            if result > 0:
                flash('Event created successfully! You can add another event below.', 'success')
                # Clear form data by redirecting back to add_event
                return redirect(url_for('add_event'))
            else:
                flash('Failed to create event. Please check your data and try again.', 'error')

        except Exception as e:
            logger.error(f"Add event error: {e}")
            flash(f'Error creating event: {str(e)}', 'error')

    # GET request - fetch places for dropdown
    try:
        places = db_manager.execute_query("SELECT PlaceID, Name, Address FROM places ORDER BY Name")
        return render_template('add_event.html', places=places)
    except Exception as e:
        logger.error(f"Error fetching places: {e}")
        flash('Error loading places', 'error')
        return render_template('add_event.html', places=[])

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/manage_permissions')
@require_admin
def manage_permissions():
    """Admin interface to manage user permissions"""
    try:
        users = db_manager.execute_query("""
            SELECT m.MemberID, m.Username, m.FirstName, m.LastName, m.Email, p.CanEditMembers, p.CanPostEvents, p.CanManageVehicles
            FROM members m
            LEFT JOIN permissions p ON m.MemberID = p.MemberID
            ORDER BY m.Username
        """)

        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'email': user[4],
                'permissions': {
                    'can_edit_members': bool(user[5]),
                    'can_post_events': bool(user[6]),
                    'can_manage_vehicles': bool(user[7])
                }
            })

        return render_template('manage_permissions.html', users=user_list)
    except Exception as e:
        logger.error(f"Manage permissions error: {e}")
        flash('Error loading permissions page', 'error')
        return redirect(url_for('dashboard'))

@app.route('/update_permissions', methods=['POST'])
@require_admin
def update_permissions():
    """Update user permissions via AJAX"""
    try:
        user_id = request.form.get('user_id')
        can_edit_members = request.form.get('can_edit_members') == 'on'
        can_post_events = request.form.get('can_post_events') == 'on'
        can_manage_vehicles = request.form.get('can_manage_vehicles') == 'on'

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID is required'})

        # Check if permissions record exists
        existing = db_manager.execute_query(
            "SELECT * FROM permissions WHERE MemberID = ?",
            [user_id]
        )

        if existing:
            # Update existing permissions
            update_query = """
                UPDATE permissions
                SET CanEditMembers = ?, CanPostEvents = ?, CanManageVehicles = ?
                WHERE MemberID = ?
            """
            result = db_manager.execute_query(
                update_query,
                [can_edit_members, can_post_events, can_manage_vehicles, user_id]
            )
        else:
            # Insert new permissions record
            insert_query = """
                INSERT INTO permissions (MemberID, CanEditMembers, CanPostEvents, CanManageVehicles)
                VALUES (?, ?, ?, ?)
            """
            result = db_manager.execute_query(
                insert_query,
                [user_id, can_edit_members, can_post_events, can_manage_vehicles]
            )

        if result > 0:
            logger.info(f"Permissions updated for user ID {user_id}")
            return jsonify({'success': True, 'message': 'Permissions updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update permissions'})

    except Exception as e:
        logger.error(f"Update permissions error: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while updating permissions'})

@app.route('/profile')
@login_required
def profile():
    """Display user profile"""
    try:
        user = db_manager.execute_query(
            "SELECT * FROM members WHERE MemberID = ?",
            [session['user_id']]
        )
        
        if user:
            user_data = user[0]
            return render_template('profile.html', user=user_data, current_user=user_data)
        else:
            flash('User not found', 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logger.error(f"Profile error: {e}")
        flash('Error loading profile', 'error')
        return redirect(url_for('dashboard'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        try:
            first_name = request.form['first_name'].strip()
            last_name = request.form['last_name'].strip()
            email = request.form['email'].strip()
            phone = request.form.get('phone', '').strip()
            bio = request.form.get('bio', '').strip()
            profile_picture = request.form.get('profile_picture', '').strip()
            location = request.form.get('location', '').strip()

            # Handle file upload
            if 'profile_picture_file' in request.files:
                file = request.files['profile_picture_file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    profile_picture = f'/static/uploads/{filename}'

            # Validate input
            if not all([first_name, last_name, email]):
                flash('First name, last name, and email are required', 'error')
                return redirect(url_for('edit_profile'))

            # Update user
            update_query = """
                UPDATE members
                SET FirstName = ?, LastName = ?, Email = ?, Phone = ?, Bio = ?, ProfilePicture = ?, Location = ?
                WHERE MemberID = ?
            """

            result = db_manager.execute_query(
                update_query,
                [first_name, last_name, email, phone, bio, profile_picture, location, session['user_id']]
            )

            if result:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Failed to update profile', 'error')

        except Exception as e:
            logger.error(f"Edit profile error: {e}")
            flash('Error updating profile', 'error')
    
    # GET request - load current user data
    try:
        user = db_manager.execute_query(
            "SELECT * FROM members WHERE MemberID = ?",
            [session['user_id']]
        )
        
        if user:
            return render_template('edit_profile.html', user=user[0], current_user=user[0])
        else:
            flash('User not found', 'error')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        logger.error(f"Edit profile load error: {e}")
        flash('Error loading profile', 'error')
        return redirect(url_for('dashboard'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        try:
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            # Validate passwords
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('change_password'))
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('change_password'))
            
            # Get current user
            user = db_manager.execute_query(
                "SELECT * FROM members WHERE MemberID = ?",
                [session['user_id']]
            )
            
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('dashboard'))
            
            # Verify current password
            if not check_password_hash(user[0][2], current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('change_password'))
            
            # Update password
            update_query = """
                UPDATE members 
                SET Password = ?
                WHERE MemberID = ?
            """
            
            result = db_manager.execute_query(
                update_query,
                [generate_password_hash(new_password), session['user_id']]
            )
            
            if result > 0:
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Failed to change password', 'error')
                
        except Exception as e:
            logger.error(f"Change password error: {e}")
            flash('Error changing password', 'error')
    
    return render_template('change_password.html')

# Global variables for ngrok tunnel management
ngrok_process = None
public_url = None

@app.route('/ticket_dashboard')
@login_required
@require_admin
def ticket_dashboard():
    """Display ticket dashboard with analytics and management - Admin Only"""
    try:
        # Get ticket statistics
        total_tickets = db_manager.execute_query("SELECT COUNT(*) FROM tickets")[0][0]

        valid_tickets = db_manager.execute_query(
            "SELECT COUNT(*) FROM tickets WHERE Status = 'valid'"
        )[0][0]

        used_tickets = db_manager.execute_query(
            "SELECT COUNT(*) FROM tickets WHERE Status = 'used'"
        )[0][0]

        expired_tickets = db_manager.execute_query(
            "SELECT COUNT(*) FROM tickets WHERE Status = 'expired'"
        )[0][0]

        # Calculate total revenue
        revenue_result = db_manager.execute_query(
            "SELECT SUM(Price) FROM tickets WHERE Status IN ('valid', 'used')"
        )[0][0]
        total_revenue = revenue_result if revenue_result else 0

        # Get recent tickets with event info
        tickets = db_manager.execute_query("""
            SELECT t.*, e.Title as EventTitle, e.Location as EventLocation
            FROM tickets t
            LEFT JOIN events e ON t.EventID = e.EventID
            ORDER BY t.PurchaseDate DESC
            LIMIT 10
        """)

        return render_template('ticket_dashboard.html',
                             total_tickets=total_tickets,
                             valid_tickets=valid_tickets,
                             used_tickets=used_tickets,
                             expired_tickets=expired_tickets,
                             total_revenue=total_revenue,
                             tickets=tickets)

    except Exception as e:
        logger.error(f"Ticket dashboard error: {e}")
        flash('Error loading ticket dashboard', 'error')
        return redirect(url_for('dashboard'))

@app.route('/server_control', methods=['GET', 'POST'])
@require_admin
def server_control():
    """Admin dashboard to control server public/private access"""
    global ngrok_process, public_url

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'start_public':
            try:
                # Check if tunnel is already running
                if ngrok_process and ngrok_process.poll() is None:
                    flash('Tunnel is already running!', 'warning')
                    return redirect(url_for('server_control'))

                # Start ngrok tunnel
                logger.info("Starting ngrok tunnel...")
                ngrok_process = subprocess.Popen(
                    ['ngrok', 'http', '5000'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Wait for ngrok to start and get URL
                public_url = None
                max_attempts = 5
                for attempt in range(max_attempts):
                    time.sleep(2)  # Wait 2 seconds between attempts

                    try:
                        # Try multiple methods to get the public URL
                        result = subprocess.run(
                            ['ngrok', 'api', 'tunnels'],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                        if result.returncode == 0:
                            import json
                            tunnels = json.loads(result.stdout)
                            if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                                public_url = tunnels['tunnels'][0]['public_url']
                                logger.info(f"Public URL retrieved: {public_url}")
                                break

                        # Alternative method: check ngrok web interface
                        result2 = subprocess.run(
                            ['curl', '-s', 'http://127.0.0.1:4040/api/tunnels'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )

                        if result2.returncode == 0:
                            import json
                            tunnels = json.loads(result2.stdout)
                            if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                                public_url = tunnels['tunnels'][0]['public_url']
                                logger.info(f"Public URL retrieved via web interface: {public_url}")
                                break

                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                        continue

                if public_url:
                    flash(f'Server is now public at: {public_url}', 'success')
                    logger.info(f"Tunnel started successfully with URL: {public_url}")
                else:
                    flash('Tunnel started successfully! Check ngrok web interface at http://127.0.0.1:4040 for the public URL.', 'warning')
                    logger.info("Tunnel started but URL retrieval failed - check ngrok web interface")

            except Exception as e:
                logger.error(f"Error starting tunnel: {e}")
                flash(f'Failed to start tunnel: {str(e)}', 'error')

        elif action == 'stop_public':
            try:
                if ngrok_process and ngrok_process.poll() is None:
                    ngrok_process.terminate()
                    ngrok_process.wait(timeout=5)
                    ngrok_process = None
                    public_url = None
                    flash('Server is now private', 'success')
                    logger.info("Tunnel stopped")
                else:
                    flash('No tunnel is currently running', 'info')
            except Exception as e:
                logger.error(f"Error stopping tunnel: {e}")
                flash(f'Failed to stop tunnel: {str(e)}', 'error')

        return redirect(url_for('server_control'))

    # GET request - show current status
    tunnel_status = 'running' if (ngrok_process and ngrok_process.poll() is None) else 'stopped'

    return render_template('server_control.html',
                         tunnel_status=tunnel_status,
                         public_url=public_url)

@app.route('/add_place', methods=['GET', 'POST'])
@require_admin
def add_place():
    """Handle place creation - Admin Only"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name'].strip()
            address = request.form['address'].strip()
            place_type = request.form['type']
            description = request.form.get('description', '').strip()

            # Validate required fields
            if not all([name, address, place_type]):
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('add_place'))

            # Insert new place
            insert_query = """
                INSERT INTO places (Name, Address, Type, Description, AddedBy, AddedDate)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')

            result = db_manager.execute_query(
                insert_query,
                [name, address, place_type, description, session['user_id'], current_date]
            )

            if result > 0:
                flash(f'Place "{name}" added successfully! You can add another place below.', 'success')
                # Clear form data by redirecting back to add_place
                return redirect(url_for('add_place'))
            else:
                flash('Failed to add place', 'error')

        except Exception as e:
            logger.error(f"Add place error: {e}")
            flash('Error adding place. Please try again.', 'error')

    return render_template('add_place.html')

# Forgot Password functionality
reset_tokens = {}  # In production, store in database with expiration

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Please enter your email address', 'error')
            return render_template('forgot_password.html')

        try:
            # Check if user exists
            user = db_manager.execute_query(
                "SELECT MemberID, Username FROM members WHERE Email = ?",
                [email]
            )

            if user:
                # Generate reset token
                token = secrets.token_urlsafe(32)
                reset_tokens[token] = {
                    'user_id': user[0][0],
                    'username': user[0][1],
                    'expires': datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
                }

                # Send reset email
                reset_url = url_for('reset_password', token=token, _external=True)
                msg = Message(
                    'Password Reset Request',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )
                msg.body = f"""Hello {user[0][1]},

You have requested to reset your password. Please click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
Community Management System
"""

                try:
                    mail.send(msg)
                    flash('Password reset link has been sent to your email address', 'success')
                    logger.info(f"Password reset email sent to {email}")
                except Exception as mail_error:
                    logger.error(f"Failed to send password reset email to {email}: {mail_error}")
                    flash('There was an error sending the email. Please try again later.', 'error')
            else:
                # Don't reveal if email exists or not for security
                flash('If an account with that email exists, a password reset link has been sent', 'info')

        except Exception as e:
            logger.error(f"Forgot password error: {e}")
            flash('An error occurred. Please try again later.', 'error')

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset"""
    # Check if token is valid
    if token not in reset_tokens:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('login'))

    token_data = reset_tokens[token]

    # Check if token has expired
    if datetime.now() > token_data['expires']:
        del reset_tokens[token]
        flash('Reset token has expired', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('reset_password.html', token=token)

        try:
            # Update password
            hashed_password = generate_password_hash(new_password)
            result = db_manager.execute_query(
                "UPDATE members SET Password = ? WHERE MemberID = ?",
                [hashed_password, token_data['user_id']]
            )

            if result > 0:
                # Remove used token
                del reset_tokens[token]
                flash('Password has been reset successfully! You can now log in with your new password.', 'success')
                logger.info(f"Password reset successful for user ID {token_data['user_id']}")
                return redirect(url_for('login'))
            else:
                flash('Failed to reset password. Please try again.', 'error')

        except Exception as e:
            logger.error(f"Reset password error: {e}")
            flash('An error occurred. Please try again later.', 'error')

    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    # Configure Flask for external access (important for tunnels)
    app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for tunnels
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Run with threaded=True for better tunnel compatibility
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)






