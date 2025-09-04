from functools import wraps
from flask import session, redirect, url_for, flash, abort
from database_manager_hybrid import db_manager

class PermissionManager:
    """Centralized permission management for the application"""
    
    @staticmethod
    def get_user_permissions(user_id):
        """Get all permissions for a specific user"""
        try:
            permissions = db_manager.execute_query(
                "SELECT * FROM permissions WHERE MemberID = ?",
                [user_id]
            )
            if permissions:
                return {
                    'can_edit_members': bool(permissions[0][2]),
                    'can_post_events': bool(permissions[0][3]),
                    'can_manage_vehicles': bool(permissions[0][4])
                }
            return None
        except Exception as e:
            print(f"Error getting permissions: {e}")
            return None
    
    @staticmethod
    def has_permission(user_id, permission_type):
        """Check if user has specific permission"""
        permissions = PermissionManager.get_user_permissions(user_id)
        if not permissions:
            return False
        
        permission_map = {
            'edit_members': 'can_edit_members',
            'post_events': 'can_post_events',
            'manage_vehicles': 'can_manage_vehicles'
        }
        
        return permissions.get(permission_map.get(permission_type, ''), False)
    
    @staticmethod
    def update_permissions(user_id, permissions_dict):
        """Update user permissions"""
        try:
            query = """
                UPDATE permissions 
                SET CanEditMembers = ?, CanPostEvents = ?, CanManageVehicles = ?
                WHERE MemberID = ?
            """
            db_manager.execute_query(
                query,
                [
                    permissions_dict.get('can_edit_members', False),
                    permissions_dict.get('can_post_events', False),
                    permissions_dict.get('can_manage_vehicles', False),
                    user_id
                ]
            )
            return True
        except Exception as e:
            print(f"Error updating permissions: {e}")
            return False
    
    @staticmethod
    def create_default_permissions(user_id):
        """Create default permissions for new user"""
        try:
            db_manager.execute_query(
                "INSERT INTO permissions (MemberID, CanEditMembers, CanPostEvents, CanManageVehicles) VALUES (?, 0, 0, 0)",
                [user_id]
            )
            return True
        except Exception as e:
            print(f"Error creating default permissions: {e}")
            return False

# Decorators for route protection
def require_permission(permission_type):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            if not PermissionManager.has_permission(session['user_id'], permission_type):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin(f):
    """Decorator to require admin permissions (CanEditMembers)"""
    return require_permission('edit_members')(f)

def get_user_role(user_id):
    """Get user role based on permissions"""
    permissions = PermissionManager.get_user_permissions(user_id)
    if not permissions:
        return 'member'
    
    if permissions['can_edit_members']:
        return 'admin'
    elif permissions['can_post_events'] or permissions['can_manage_vehicles']:
        return 'moderator'
    else:
        return 'member'
