"""
Authentication Routes
Handles user login and authentication
"""

from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from database import execute_query
from config import config
from utils.validators import validate_login_input

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint

    Request body:
    {
        "userid": "student1",
        "password_md5": "aeddf07d1ab10bd6d8dde8b778368511"
    }

    Response:
    {
        "success": true,
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "role": "student",
        "userid": "student1"
    }
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate input
        is_valid, error_message = validate_login_input(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        userid = data.get('userid')
        password_md5 = data.get('password_md5')

        # Query database for user
        user = execute_query(
            "SELECT userid, role FROM users WHERE userid = %s AND password_hash = %s",
            (userid, password_md5),
            fetch_one=True
        )

        # Check if user exists and password matches
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401

        # Create JWT token
        token_payload = {
            'userid': user['userid'],
            'role': user['role'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
        }

        token = jwt.encode(
            token_payload,
            config.JWT_SECRET,
            algorithm=config.JWT_ALGORITHM
        )

        # Return success response
        return jsonify({
            'success': True,
            'token': token,
            'role': user['role'],
            'userid': user['userid']
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error during login'
        }), 500


@auth_bp.route('/users/me', methods=['GET'])
def get_current_user():
    """
    Get current user information
    Requires authentication token

    Headers:
        Authorization: Bearer <token>

    Response:
    {
        "success": true,
        "user": {
            "userid": "student1",
            "role": "student"
        }
    }
    """
    from middleware.auth_middleware import token_required

    @token_required
    def _get_current_user(current_user):
        try:
            # Fetch user details (excluding password hash)
            user = execute_query(
                "SELECT userid, role FROM users WHERE userid = %s",
                (current_user['userid'],),
                fetch_one=True
            )

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404

            return jsonify({
                'success': True,
                'user': user
            }), 200

        except Exception as e:
            print(f"Get current user error: {e}")
            return jsonify({
                'success': False,
                'error': 'Server error'
            }), 500

    return _get_current_user()