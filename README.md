# SuliStreetMeet - Full-Stack Car Community Application

A modern, animated green-themed full-stack application for a private car community called SuliStreetMeet.

## Features

### Backend (Python Flask)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with role-based permissions
- **API Endpoints**: RESTful endpoints for all CRUD operations
- **Real-time Updates**: WebSocket support for live updates
- **Security**: Password hashing, CSRF protection, input validation

### Frontend
- **Theme**: Green neon with modern gradients and animations
- **Responsive**: Fully responsive for mobile and desktop
- **Animations**: Smooth transitions, hover effects, loading spinners
- **Components**: Reusable components with consistent styling

### Database Schema
- **Members**: User management with authentication
- **Vehicles**: Car details linked to members
- **Events**: Community events and meetups
- **Places**: Meeting spots and locations
- **Permissions**: Role-based access control

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sulistreetmeet
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. Initialize the database:
```bash
python app.py
```

6. Access the application:
- Open your browser to `http://localhost:5000`
- Register a new account or use the demo credentials

### Quick Public Access (Temporary)

For instant public access that you can stop anytime:

#### Windows Users (Simplest)
```bash
# Just double-click this file:
start_tunnel.bat
```

#### Python Script
```bash
# Run this script:
python setup_tunnel.py
```

#### Manual Method
```bash
# Start your Flask app first:
python app.py

# In another terminal, run:
python setup_tunnel.py
```

**Note**: Your website becomes private automatically when you close the terminal/command prompt.

### Getting a Custom Domain (sulistreetmeet.com)

To get a custom domain like `sulistreetmeet.com`:

#### Free Options (Temporary)
- **Free Subdomains**: Use services like `sulistreetmeet.free.nf` or `sulistreetmeet.great-site.net`
- **GitHub Pages**: `sulistreetmeet.github.io` (but requires static site)
- **Netlify**: Free subdomain or bring your own domain

#### Paid Domain Registration ($10-15/year)
1. **GoDaddy**: https://godaddy.com - Search for "sulistreetmeet.com"
2. **Namecheap**: https://namecheap.com - Often cheaper than GoDaddy
3. **Google Domains**: https://domains.google - Clean interface
4. **Hover**: https://hover.com - Good customer service

#### Steps to Get sulistreetmeet.com:
1. Check if available: Search on any registrar above
2. Register the domain ($10-15/year)
3. Point it to your hosting (Heroku, Railway, etc.)
4. Update DNS records (A record or CNAME)

#### Cost Breakdown:
- Domain: $10-15/year
- Hosting: Free (Heroku, Railway, Vercel)
- SSL Certificate: Free (included with hosting)

**Pro Tip**: Use Namecheap for domains - they often have better prices and free privacy protection!

## Server Deployment

### Temporary Public Access

Since ngrok may block certain IP addresses, here are multiple alternatives for making your local server publicly accessible:

#### Option 1: ngrok (May be blocked by IP)
1. **Install ngrok**:
   - Download from https://ngrok.com/download
   - Extract `ngrok.exe` to your project directory

2. **Access Server Control Dashboard**:
   - Login as admin
   - Navigate to `/server_control`
   - Click "Make Server Public" to start ngrok tunnel
   - Share the generated public URL with others

#### Option 2: LocalTunnel (Recommended Alternative)
1. **Automatic Setup**:
   ```bash
   python localtunnel_setup.py
   ```

2. **Manual Setup**:
   - Install Node.js from https://nodejs.org/
   - Run: `npm install -g localtunnel`

3. **Usage**:
   ```bash
   # Start your Flask app first
   python app.py

   # In a new terminal
   lt --port 5000
   ```

#### Option 3: Serveo SSH Tunnel (Simplest)
No installation required! Uses built-in Windows SSH:

1. **Using Batch File**:
   - Double-click `serveo_tunnel.bat`

2. **Using PowerShell**:
   - Run `.\serveo_tunnel.ps1`

3. **Manual Command**:
   ```bash
   ssh -R 80:localhost:5000 serveo.net
   ```

#### Option 4: Change Network (Quick Fix)
- Use mobile hotspot
- Connect to different WiFi
- Use VPN to change IP address

### Security Notes for Public Access
- All methods provide temporary public access
- URLs change each time you restart the tunnel
- Consider authentication requirements for public access
- Use HTTPS URLs when available for security

### Free Hosting on Heroku

For permanent free hosting:

1. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Prepare for Deployment**:
   ```bash
   # Login to Heroku
   heroku login

   # Create Heroku app
   heroku create your-app-name

   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set FLASK_ENV=production
   ```

3. **Deploy**:
   ```bash
   # Add files to git
   git add .
   git commit -m "Deploy to Heroku"

   # Deploy
   git push heroku main
   ```

4. **Access Your App**:
   - Your app will be available at `https://your-app-name.herokuapp.com`
   - Free tier includes 550-1000 hours/month
   - Database is SQLite (suitable for small applications)

### Environment Variables for Production

Set these in your `.env` file or Heroku config:

```
SECRET_KEY=your-secure-random-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///sulistreetmeet.db
```

**Note**: For production, consider using PostgreSQL instead of SQLite for better performance and reliability.

## Project Structure

```
sulistreetmeet/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Dashboard
│   ├── members.html      # Members management
│   ├── vehicles.html     # Vehicles management
│   ├── events.html       # Events management
│   └── places.html       # Places management
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # JavaScript functionality
└── README.md             # This file
```

## Usage

### Admin Panel
- Access `/dashboard` after login
- Manage members, vehicles, events, and places
- Set user permissions and roles

### User Features
- Register and login
- Add vehicles to your profile
- Create and join events
- Discover new places
- Connect with other members

### API Endpoints
- `GET /api/members` - List all members
- `POST /api/members` - Create new member
- `GET /api/vehicles` - List all vehicles
- `POST /api/vehicles` - Add new vehicle
- `GET /api/events` - List all events
- `POST /api/events` - Create new event

## Development

### Adding New Features
1. Create new routes in `app.py`
2. Add corresponding templates in `templates/`
3. Update static files as needed
4. Test thoroughly

### Database Migrations
```bash
# After model changes
python app.py
```

### Environment Variables
Create a `.env` file with:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///sulistreetmeet.db
FLASK_ENV=development
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, email support@sulistreetmeet.com or create an issue in the repository.
