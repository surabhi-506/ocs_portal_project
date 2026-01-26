"""
Student Routes
Handles student-specific operations
"""
from flask import Blueprint, request, jsonify
from database import execute_query
from middleware.auth_middleware import token_required, role_required
from utils.validators import validate_apply_input

# Create blueprint
student_bp = Blueprint('student', __name__)


@student_bp.route('/profiles', methods=['GET'])
@token_required
def get_all_profiles(current_user):
    """
    Get all available job profiles
    CONSTRAINT: Returns 403 if student has a 'Selected' or 'Accepted' status
    """
    try:
        userid = current_user['userid']

        # 1. LOGIC FIX: Check if student is "locked" by a Selected/Accepted offer
        lock_check = execute_query(
            "SELECT status FROM application WHERE entry_number = %s AND status IN ('Selected', 'Accepted')",
            (userid,),
            fetch_one=True
        )

        if lock_check:
            # If locked, deny access to the profiles list
            return jsonify({
                'success': False,
                'error': 'Access denied: You have a pending or accepted offer.',
                'code': 'LOCKED_BY_OFFER'
            }), 403

        # 2. If not locked, fetch profiles
        profiles = execute_query(
            """
            SELECT profile_code, recruiter_email, company_name, designation 
            FROM profile 
            ORDER BY profile_code
            """,
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'profiles': profiles
        }), 200

    except Exception as e:
        print(f"Get profiles error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@student_bp.route('/applications/mine', methods=['GET'])
@token_required
@role_required(['student'])
def get_my_applications(current_user):
    """
    Get current student's applications
    Used by Frontend to check if they have a 'Selected' offer to display
    """
    try:
        applications = execute_query(
            """
            SELECT a.profile_code, a.entry_number, a.status,
                   p.company_name, p.designation, p.recruiter_email
            FROM application a
            JOIN profile p ON a.profile_code = p.profile_code
            WHERE a.entry_number = %s
            ORDER BY a.profile_code
            """,
            (current_user['userid'],),
            fetch_all=True
        )

        return jsonify({
            'success': True,
            'applications': applications
        }), 200

    except Exception as e:
        print(f"Get applications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@student_bp.route('/apply', methods=['POST'])
@token_required
@role_required(['student'])
def apply_to_profile(current_user):
    """
    Apply to a job profile
    CONSTRAINT: Blocks application if status is 'Selected' or 'Accepted'
    """
    try:
        data = request.get_json()

        # Validate input
        is_valid, error_message = validate_apply_input(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400

        profile_code = data.get('profile_code')
        userid = current_user['userid']

        # LOGIC FIX: Check if student has ANY 'Accepted' OR 'Selected' offer
        # The original code only checked 'Accepted'. We must add 'Selected'.
        lock_check = execute_query(
            "SELECT status FROM application WHERE entry_number = %s AND status IN ('Accepted', 'Selected')",
            (userid,),
            fetch_one=True
        )

        if lock_check:
            return jsonify({
                'success': False,
                'error': f"Cannot apply: You have a '{lock_check['status']}' application. Please resolve it first."
            }), 400

        # Check if student already applied to this specific profile
        existing_application = execute_query(
            "SELECT * FROM application WHERE profile_code = %s AND entry_number = %s",
            (profile_code, userid),
            fetch_one=True
        )

        if existing_application:
            return jsonify({
                'success': False,
                'error': 'You have already applied to this position'
            }), 400

        # Check if profile exists
        profile = execute_query(
            "SELECT * FROM profile WHERE profile_code = %s",
            (profile_code,),
            fetch_one=True
        )

        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Create application
        execute_query(
            "INSERT INTO application (profile_code, entry_number, status) VALUES (%s, %s, %s)",
            (profile_code, userid, 'Applied')
        )

        return jsonify({
            'success': True,
            'message': 'Application submitted successfully'
        }), 201

    except Exception as e:
        print(f"Apply error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@student_bp.route('/application/accept', methods=['POST'])
@token_required
@role_required(['student'])
def accept_offer(current_user):
    """
    Accept a selected offer
    Transitions status: Selected -> Accepted
    """
    try:
        data = request.get_json()
        profile_code = data.get('profile_code')
        userid = current_user['userid']

        if not profile_code:
            return jsonify({
                'success': False,
                'error': 'profile_code is required'
            }), 400

        # Check if application exists and is in 'Selected' status
        application = execute_query(
            """
            SELECT a.*, p.company_name, p.designation 
            FROM application a
            JOIN profile p ON a.profile_code = p.profile_code
            WHERE a.profile_code = %s AND a.entry_number = %s
            """,
            (profile_code, userid),
            fetch_one=True
        )

        if not application:
            return jsonify({
                'success': False,
                'error': 'Application not found'
            }), 404

        if application['status'] != 'Selected':
            return jsonify({
                'success': False,
                'error': 'Can only accept applications with Selected status'
            }), 400

        # Update status to Accepted
        execute_query(
            "UPDATE application SET status = %s WHERE profile_code = %s AND entry_number = %s",
            ('Accepted', profile_code, userid)
        )

        return jsonify({
            'success': True,
            'message': 'Offer accepted successfully',
            'company_name': application['company_name'],
            'designation': application['designation']
        }), 200

    except Exception as e:
        print(f"Accept offer error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500


@student_bp.route('/application/reject', methods=['POST'])
@token_required
@role_required(['student'])
def reject_offer(current_user):
    """
    Reject a selected offer
    Transitions status: Selected -> Not Selected
    """
    try:
        data = request.get_json()
        profile_code = data.get('profile_code')
        userid = current_user['userid']

        if not profile_code:
            return jsonify({
                'success': False,
                'error': 'profile_code is required'
            }), 400

        # Check if application exists and is in 'Selected' status
        application = execute_query(
            "SELECT * FROM application WHERE profile_code = %s AND entry_number = %s",
            (profile_code, userid),
            fetch_one=True
        )

        if not application:
            return jsonify({
                'success': False,
                'error': 'Application not found'
            }), 404

        if application['status'] != 'Selected':
            return jsonify({
                'success': False,
                'error': 'Can only reject applications with Selected status'
            }), 400

        # Update status to Not Selected
        execute_query(
            "UPDATE application SET status = %s WHERE profile_code = %s AND entry_number = %s",
            ('Not Selected', profile_code, userid)
        )

        return jsonify({
            'success': True,
            'message': 'Offer rejected'
        }), 200

    except Exception as e:
        print(f"Reject offer error: {e}")
        return jsonify({
            'success': False,
            'error': 'Server error'
        }), 500