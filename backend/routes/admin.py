"""
Admin Routes
Handles admin-specific operations
"""

from flask import Blueprint, jsonify
from database import execute_query
from middleware.auth_middleware import token_required, role_required

# Create blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_users(current_user):
    """
    Get all users (excluding password hashes)
    Admin only

    Response:
    {
        "success": true,
        "users": [
            {
                "userid": "admin",
                "role": "admin"
            },
            ...
        ]
    }
    """
    try:
        users = execute_query(
            "SELECT userid, role FROM users ORDER BY role, userid",
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'users': users
        }), 200

    except Exception as e:
        print(f"Get all users error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@admin_bp.route('/profiles', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_profiles_admin(current_user):
    """
    Get all profiles
    Admin only

    Response:
    {
        "success": true,
        "profiles": [...]
    }
    """
    try:
        profiles = execute_query(
            "SELECT * FROM profile ORDER BY profile_code",
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'profiles': profiles
        }), 200

    except Exception as e:
        print(f"Get all profiles error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@admin_bp.route('/applications', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_applications(current_user):
    """
    Get all applications
    Admin only

    Response:
    {
        "success": true,
        "applications": [...]
    }
    """
    try:
        applications = execute_query(
            """
            SELECT a.profile_code, a.entry_number, a.status,
                   p.company_name, p.designation, p.recruiter_email
            FROM application a
            JOIN profile p ON a.profile_code = p.profile_code
            ORDER BY a.profile_code, a.entry_number
            """,
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'applications': applications
        }), 200

    except Exception as e:
        print(f"Get all applications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500