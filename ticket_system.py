import os
import qrcode
import io
import secrets
import base64
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, session, send_file, redirect, url_for, Response
from database_manager_hybrid import db_manager
from PIL import Image

# Create blueprint for ticket system
ticket_bp = Blueprint('ticket', __name__)

# Initialize ticket database table
def init_ticket_table():
    """Initialize the tickets table if it doesn't exist"""
    try:
        # Check if tickets table exists
        if not db_manager.check_table_exists('tickets'):
            # Create tickets table
            create_query = """
                CREATE TABLE tickets (
                    TicketID TEXT PRIMARY KEY,
                    EventID INTEGER,
                    BuyerName TEXT NOT NULL,
                    BuyerEmail TEXT NOT NULL,
                    BuyerPhone TEXT,
                    Price DOUBLE,
                    PurchaseDate TEXT NOT NULL,
                    QRCode MEMO,
                    Status TEXT DEFAULT 'valid',
                    ScannedAt TEXT,
                    ScannedBy TEXT,
                    FOREIGN KEY (EventID) REFERENCES events(EventID)
                )
            """
            db_manager.execute_query(create_query)
            print("Tickets table created successfully")
    except Exception as e:
        print(f"Error creating tickets table: {e}")

# Generate QR code for ticket
def generate_qr_code(ticket_id):
    """Generate QR code for ticket validation"""
    try:
        # Create smaller QR code to avoid database size limits
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,  # Smaller box size
            border=2,    # Smaller border
        )
        qr.add_data(f"TICKET:{ticket_id}")
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for storage
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return qr_code_base64
    except:
        # If QR code generation fails, just store the ticket ID
        return ticket_id

# Routes
@ticket_bp.route('/buy_ticket')
def buy_ticket():
    """Display ticket purchase page"""
    try:
        # Get all events for ticket purchase
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        events = db_manager.execute_query("""
            SELECT EventID, Title, EventDate, Location, Description
            FROM events
            WHERE EventDate >= ?
            ORDER BY EventDate ASC
        """, [today])

        return render_template('buy_ticket_simple.html', events=events)
    except Exception as e:
        print(f"Error loading buy ticket page: {e}")
        flash('Error loading ticket purchase page', 'error')
        return redirect(url_for('events'))

@ticket_bp.route('/buy_ticket/<int:event_id>', methods=['GET', 'POST'])
def purchase_ticket(event_id):
    """Handle ticket purchase for specific event"""
    # Get event details (simplified)
    event = db_manager.execute_query("""
        SELECT EventID, Title, EventDate, Location, Description
        FROM events
        WHERE EventID = ?
    """, [event_id])

    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('ticket.buy_ticket'))

    event = event[0]

    if request.method == 'POST':
        # Get form data with defaults
        buyer_name = request.form.get('buyer_name', '').strip() or 'Guest'
        buyer_email = request.form.get('buyer_email', '').strip() or 'guest@example.com'
        buyer_phone = request.form.get('buyer_phone', '').strip() or ''
        price_str = request.form.get('price', '10.00')

        # Generate unique ticket ID
        ticket_id = secrets.token_hex(8).upper()

        # Store just the ticket ID - QR code will be generated on demand
        qr_code_data = ticket_id

        # Save ticket to database
        purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            price = float(price_str)
        except:
            price = 10.00

        insert_query = """
            INSERT INTO tickets (TicketID, EventID, BuyerName, BuyerEmail, BuyerPhone, Price, PurchaseDate, QRCode, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'valid')
        """

        db_manager.execute_query(insert_query, [
            ticket_id, event_id, buyer_name, buyer_email, buyer_phone,
            price, purchase_date, qr_code_data
        ])

        # Always succeed and redirect to ticket display
        flash('Ticket purchased successfully!', 'success')
        return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))

    # GET request - show purchase form
    return render_template('purchase_ticket.html',
                         event=event,
                         buyer_name=session.get('username', ''),
                         buyer_email='')

@ticket_bp.route('/ticket/<ticket_id>')
def view_ticket(ticket_id):
    """Display ticket details"""
    # Get ticket details (simplified)
    ticket = db_manager.execute_query("""
        SELECT t.*, e.Title as EventName, e.EventDate, e.Location
        FROM tickets t
        JOIN events e ON t.EventID = e.EventID
        WHERE t.TicketID = ?
    """, [ticket_id])

    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('ticket.buy_ticket'))

    ticket = ticket[0]

    # Get event details
    event = db_manager.execute_query("""
        SELECT Title, EventDate, Location
        FROM events
        WHERE EventID = ?
    """, [ticket[1]])  # EventID is at index 1

    if event:
        event = event[0]
    else:
        event = ['Unknown Event', 'Unknown Date', 'Unknown Location']

    return render_template('view_ticket.html',
                         ticket=ticket,
                         event=event,
                         qr_code_url=f"/ticket/qr/{ticket_id}")

@ticket_bp.route('/ticket/qr/<ticket_id>')
def get_qr_code(ticket_id):
    """Serve QR code image - generated on demand"""
    try:
        # Verify ticket exists
        ticket = db_manager.execute_query("""
            SELECT TicketID FROM tickets WHERE TicketID = ?
        """, [ticket_id])

        if not ticket:
            return Response("Ticket not found", status=404, mimetype='text/plain')

        # Generate QR code on the fly
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"TICKET:{ticket_id}")
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert PIL image to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        image_bytes = buffer.getvalue()

        # Return as downloadable file
        response = Response(image_bytes, mimetype='image/png')
        response.headers.set('Content-Disposition', f'attachment; filename=ticket_{ticket_id}.png')
        response.headers.set('Content-Type', 'image/png')
        return response

    except Exception as e:
        print(f"Error serving QR code: {e}")
        return Response("Error loading QR code", status=500, mimetype='text/plain')

@ticket_bp.route('/api/scan_ticket', methods=['POST'])
def scan_ticket():
    """API endpoint for scanning tickets"""
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id', '').replace('TICKET:', '')

        if not ticket_id:
            return jsonify({'success': False, 'error': 'Invalid ticket ID'})

        # Get ticket details
        ticket = db_manager.execute_query("""
            SELECT t.*, e.Title as EventName, e.EventDate
            FROM tickets t
            JOIN events e ON t.EventID = e.EventID
            WHERE t.TicketID = ?
        """, [ticket_id])

        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'})

        ticket = ticket[0]

        # Check ticket status
        if ticket[8] == 'used':  # Status is at index 8
            return jsonify({
                'success': False,
                'error': 'Ticket has already been used',
                'ticket': {
                    'id': ticket[0],
                    'buyer_name': ticket[2],
                    'event_name': ticket[9],  # EventName
                    'status': ticket[8],
                    'scanned_at': ticket[9] if len(ticket) > 9 else None
                }
            })

        if ticket[8] == 'expired':
            return jsonify({
                'success': False,
                'error': 'Ticket has expired',
                'ticket': {
                    'id': ticket[0],
                    'buyer_name': ticket[2],
                    'event_name': ticket[9],
                    'status': ticket[8]
                }
            })

        # Mark ticket as used
        scanned_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query = """
            UPDATE tickets
            SET Status = 'used', ScannedAt = ?, ScannedBy = ?
            WHERE TicketID = ?
        """

        db_manager.execute_query(update_query, [
            scanned_at,
            session.get('username', 'Scanner'),
            ticket_id
        ])

        return jsonify({
            'success': True,
            'message': 'Ticket validated successfully',
            'ticket': {
                'id': ticket[0],
                'buyer_name': ticket[2],
                'event_name': ticket[9],
                'event_date': ticket[10],
                'scanned_at': scanned_at
            }
        })

    except Exception as e:
        print(f"Error scanning ticket: {e}")
        return jsonify({'success': False, 'error': 'Server error'})

@ticket_bp.route('/scan_ticket')
def scan_ticket_page():
    """Display ticket scanning page"""
    return render_template('scan_ticket.html')

@ticket_bp.route('/dashboard')
def ticket_dashboard():
    """Modern ticket dashboard with overview and analytics"""
    try:
        # Get all tickets with event details
        tickets = db_manager.execute_query("""
            SELECT t.*, e.Title as EventName, e.EventDate, e.Location
            FROM tickets t
            LEFT JOIN events e ON t.EventID = e.EventID
            ORDER BY t.PurchaseDate DESC
        """)

        # Calculate statistics
        total_tickets = len(tickets) if tickets else 0
        valid_tickets = len([t for t in tickets if t[8] == 'valid']) if tickets else 0
        used_tickets = len([t for t in tickets if t[8] == 'used']) if tickets else 0
        expired_tickets = len([t for t in tickets if t[8] == 'expired']) if tickets else 0

        # Get recent tickets (last 10)
        recent_tickets = tickets[:10] if tickets else []

        # Calculate revenue
        total_revenue = sum(float(t[5]) for t in tickets if t[5]) if tickets else 0

        return render_template('ticket_dashboard.html',
                             tickets=recent_tickets,
                             total_tickets=total_tickets,
                             valid_tickets=valid_tickets,
                             used_tickets=used_tickets,
                             expired_tickets=expired_tickets,
                             total_revenue=total_revenue)

    except Exception as e:
        print(f"Error loading ticket dashboard: {e}")
        return render_template('ticket_dashboard.html',
                             tickets=[],
                             total_tickets=0,
                             valid_tickets=0,
                             used_tickets=0,
                             expired_tickets=0,
                             total_revenue=0)

# Initialize the ticket system
def init_app(app):
    """Initialize ticket system with Flask app"""
    init_ticket_table()
    app.register_blueprint(ticket_bp, url_prefix='/ticket')

    # Add ticket routes to main app
    @app.route('/buy_ticket')
    def buy_ticket_redirect():
        return redirect(url_for('ticket.buy_ticket'))

    @app.route('/buy_ticket/<int:event_id>')
    def buy_ticket_event_redirect(event_id):
        return redirect(url_for('ticket.purchase_ticket', event_id=event_id))

    @app.route('/api/purchase_ticket', methods=['POST'])
    def purchase_ticket_api():
        """API endpoint for ticket purchase (for AJAX requests)"""
        try:
            data = request.get_json()

            # Generate ticket
            ticket_id = secrets.token_hex(8).upper()

            # Save to database - store just ticket ID, QR code generated on demand
            purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            insert_query = """
                INSERT INTO tickets (TicketID, EventID, BuyerName, BuyerEmail, BuyerPhone, Price, PurchaseDate, QRCode, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'valid')
            """

            db_manager.execute_query(insert_query, [
                ticket_id, data['event_id'], data['buyer_name'], data['buyer_email'],
                data.get('buyer_phone', ''), float(data['price']), purchase_date, ticket_id
            ])

            # Get event details
            event = db_manager.execute_query("""
                SELECT Title, EventDate, Location FROM events WHERE EventID = ?
            """, [data['event_id']])

            if event:
                event = event[0]
                return jsonify({
                    'success': True,
                    'ticket': {
                        'ticket_id': ticket_id,
                        'event_name': event[0],
                        'event_date': event[1],
                        'buyer_name': data['buyer_name'],
                        'price': data['price'],
                        'qr_code_url': f"/ticket/qr/{ticket_id}",
                        'status': 'valid'
                    }
                })

            return jsonify({'success': False, 'error': 'Event not found'})

        except Exception as e:
            print(f"Error in ticket purchase API: {e}")
            return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # For testing
    init_ticket_table()
    print("Ticket system initialized")
