# Database Configuration Guide

## Hybrid Database Approach

This application uses a **hybrid database approach** that allows you to:
- Use **MS Access** for local development (Windows)
- Automatically switch to **SQLite** for deployment (Render/Linux)

## How It Works

The `database_manager_hybrid.py` file automatically detects the environment:

### Local Development (Windows)
- Uses your existing MS Access database
- Requires: `pywin32`, `sqlalchemy-access`, `jaydebeapi`
- Install with: `pip install pywin32 sqlalchemy-access jaydebeapi`

### Deployment (Render/Linux)
- Automatically switches to SQLite
- No additional dependencies needed
- Your data will be migrated to SQLite format

## Setup Instructions

### For Local Development

1. **Install MS Access dependencies:**
   ```bash
   pip install pywin32 sqlalchemy-access jaydebeapi
   ```

2. **Ensure your MS Access database is accessible** at the expected location

3. **Run the application normally:**
   ```bash
   python app.py
   ```

### For Deployment

1. **No changes needed!** The system automatically detects deployment environment

2. **First deployment:** The system will create SQLite database and migrate your schema

3. **Data migration:** You'll need to manually migrate your existing data from Access to SQLite

## Database Managers

### Files Overview
- `database_manager.py` - MS Access implementation
- `database_manager_sqlite.py` - SQLite implementation
- `database_manager_hybrid.py` - Hybrid manager (use this)

### Usage
```python
from database_manager_hybrid import db_manager

# Works the same regardless of underlying database
users = db_manager.execute_query("SELECT * FROM members")
```

## Environment Detection

The hybrid manager checks these environment variables:
- `FLASK_ENV=production` → Uses SQLite
- `RENDER=true` → Uses SQLite
- Otherwise → Uses MS Access

## Data Migration

When switching from MS Access to SQLite:

1. **Schema Migration:** Automatic (tables created with same structure)
2. **Data Migration:** Manual process required

### Migration Script
```python
# Example migration script
from database_manager import DatabaseManager  # Access
from database_manager_sqlite import SQLiteDatabaseManager  # SQLite

# Export from Access
access_db = DatabaseManager()
members = access_db.execute_query("SELECT * FROM members")

# Import to SQLite
sqlite_db = SQLiteDatabaseManager()
for member in members:
    sqlite_db.execute_query("INSERT INTO members VALUES (?, ?, ?, ...)", member)
```

## Troubleshooting

### Common Issues

1. **"MS Access not available"**
   - Install dependencies: `pip install pywin32 sqlalchemy-access jaydebeapi`
   - Ensure MS Access database file exists

2. **"SQLite database not found"**
   - Check file permissions
   - Database will be created automatically on first run

3. **Connection errors**
   - Verify database file paths
   - Check file permissions
   - Ensure database is not locked by another application

### Testing

Run the test script to verify your setup:
```bash
python test_hybrid_db.py
```

## Benefits

✅ **Seamless Development:** Use familiar MS Access locally
✅ **Easy Deployment:** No configuration changes needed
✅ **Cross-Platform:** Works on Windows (dev) and Linux (prod)
✅ **Data Integrity:** Same schema and queries work everywhere
✅ **Zero Downtime:** Automatic fallback to working database

## File Structure

```
your-project/
├── database_manager.py          # MS Access implementation
├── database_manager_sqlite.py   # SQLite implementation
├── database_manager_hybrid.py   # Hybrid manager (main entry point)
├── app.py                       # Main application (uses hybrid manager)
├── test_hybrid_db.py           # Test script
└── README_DATABASE.md          # This file
