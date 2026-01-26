"""
Recruiter Routes
Handles recruiter-specific operations
"""

from flask import Blueprint, request, jsonify
from database import execute_query
from middleware.auth_middleware import token_required, role_required
from utils.validators import validate_profile_input, validate_status_change_input

# Create blueprint
recruiter_bp = Blueprint('recruiter', __name__)


@recruiter_bp.route('/create_profile', methods=['POST'])
@token_required
@role_required(['recruiter', 'admin'])
def create_profile(current_user):
    """
    Create a new job profile
    Recruiters can only create for themselves
    Admins can create for any recruiter

    Request body:
    {
        "company_name": "TechCorp",
        "designation": "Backend Intern",
        "recruiter_email": "recruiter1@techcorp.com"  (optional, admin only)
    }

    Response:
    {
        "success": true,
        "message": "Profile created successfully",
        "profile_code": 1005
    }
    """
    try:
        data = request.get_json()

        # Validate input
        is_valid, error_message = validate_profile_input(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        company_name = data.get('company_name')
        designation = data.get('designation')

        # Determine recruiter email
        if current_user['role'] == 'admin':
            # Admin can create profile for any recruiter
            recruiter_email = data.get('recruiter_email')
            if not recruiter_email:
                return jsonify({
                    'success': False,
                    'error': 'recruiter_email is required for admin'
                }), 400

            # Verify recruiter exists
            recruiter = execute_query(
                "SELECT userid FROM users WHERE userid = %s AND role = %s",
                (recruiter_email, 'recruiter'),
                fetch_one=True
            )
            if not recruiter:
                return jsonify({
                    'success': False,
                    'error': 'Recruiter not found'
                }), 404
        else:
            # Recruiter creates for themselves
            recruiter_email = current_user['userid']

        # Insert profile
        execute_query(
            "INSERT INTO profile (recruiter_email, company_name, designation) VALUES (%s, %s, %s)",
            (recruiter_email, company_name, designation)
        )

        # Get the created profile code
        new_profile = execute_query(
            "SELECT profile_code FROM profile WHERE recruiter_email = %s AND company_name = %s AND designation = %s ORDER BY profile_code DESC LIMIT 1",
            (recruiter_email, company_name, designation),
            fetch_one=True
        )

        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'profile_code': new_profile['profile_code']
        }), 201

    except Exception as e:
        print(f"Create profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@recruiter_bp.route('/my_profiles', methods=['GET'])
@token_required
@role_required(['recruiter'])
def get_my_profiles(current_user):
    """
    Get all profiles created by current recruiter

    Response:
    {
        "success": true,
        "profiles": [...]
    }
    """
    try:
        profiles = execute_query(
            "SELECT * FROM profile WHERE recruiter_email = %s ORDER BY profile_code",
            (current_user['userid'],),
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'profiles': profiles
        }), 200

    except Exception as e:
        print(f"Get my profiles error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@recruiter_bp.route('/applications', methods=['GET'])
@token_required
@role_required(['recruiter'])
def get_recruiter_applications(current_user):
    """
    Get all applications to recruiter's profiles

    Response:
    {
        "success": true,
        "applications": [
            {
                "profile_code": 1001,
                "entry_number": "student1",
                "status": "Applied",
                "company_name": "TechCorp",
                "designation": "Backend Intern"
            },
            ...
        ]
    }
    """
    try:
        applications = execute_query(
            """
            SELECT a.profile_code, a.entry_number, a.status,
                   p.company_name, p.designation
            FROM application a
            JOIN profile p ON a.profile_code = p.profile_code
            WHERE p.recruiter_email = %s
            ORDER BY a.profile_code, a.entry_number
            """,
            (current_user['userid'],),
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'applications': applications
        }), 200

    except Exception as e:
        print(f"Get recruiter applications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@recruiter_bp.route('/application/change_status', methods=['POST'])
@token_required
@role_required(['recruiter', 'admin'])
def change_application_status(current_user):
    """
    Change application status
    Recruiters can only change status for their own profiles
    Admins can change any application status

    Request body:
    {
        "profile_code": 1001,
        "entry_number": "student1",
        "new_status": "Selected"
    }

    Response:
    {
        "success": true,
        "message": "Application status updated"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        is_valid, error_message = validate_status_change_input(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        profile_code = data.get('profile_code')
        entry_number = data.get('entry_number')
        new_status = data.get('new_status')

        # If recruiter, verify they own this profile
        if current_user['role'] == 'recruiter':
            profile = execute_query(
                "SELECT * FROM profile WHERE profile_code = %s AND recruiter_email = %s",
                (profile_code, current_user['userid']),
                fetch_one=True
            )

            if not profile:
                return jsonify({
                    'success': False,
                    'error': 'Profile not found or you do not have permission'
                }), 403

        # Check if application exists
        application = execute_query(
            "SELECT * FROM application WHERE profile_code = %s AND entry_number = %s",
            (profile_code, entry_number),
            fetch_one=True
        )

        if not application:
            return jsonify({
                'success': False,
                'error': 'Application not found'
            }), 404

        # Update status
        execute_query(
            "UPDATE application SET status = %s WHERE profile_code = %s AND entry_number = %s",
            (new_status, profile_code, entry_number)
        )

        return jsonify({
            'success': True,
            'message': 'Application status updated successfully'
        }), 200

    except Exception as e:
        print(f"Change status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500