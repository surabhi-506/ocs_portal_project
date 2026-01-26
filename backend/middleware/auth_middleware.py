"""
Authentication middleware
Verifies JWT tokens and extracts user information
"""

import jwt
from functools import wraps
from flask import request, jsonify
from config import config


def token_required(f):
    """
    Decorator to protect routes that require authentication
    Extracts and verifies JWT token from Authorization header

    Usage:
        @app.route('/api/protected')
        @token_required
        def protected_route(current_user):
            # current_user contains decoded token data
            return jsonify({'userid': current_user['userid']})
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Verify and decode token
            decoded = jwt.decode(
                token,
                config.JWT_SECRET,
                algorithms=[config.JWT_ALGORITHM]
            )

            # Pass decoded token data to the route
            current_user = decoded

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired', 'expired': True}), 401

        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Call the actual route with current_user
        return f(current_user, *args, **kwargs)

    return decorated


def role_required(allowed_roles):
    """
    Decorator to restrict routes to specific roles

    Args:
        allowed_roles (list): List of roles allowed to access this route

    Usage:
        @app.route('/api/admin/users')
        @token_required
        @role_required(['admin'])
        def admin_route(current_user):
            return jsonify({'message': 'Admin only'})
    """

    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            user_role = current_user.get('role')

            if user_role not in allowed_roles:
                return jsonify({
                    'error': f'Access denied. Required role: {", ".join(allowed_roles)}'
                }), 403

            return f(current_user, *args, **kwargs)

        return decorated

    return decorator