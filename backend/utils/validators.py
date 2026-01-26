"""
Input validation utilities
"""


def validate_login_input(data):
    """
    Validate login request data

    Args:
        data (dict): Request data with userid and password_md5

    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"

    userid = data.get('userid')
    password_md5 = data.get('password_md5')

    if not userid:
        return False, "userid is required"

    if not password_md5:
        return False, "password_md5 is required"

    if len(password_md5) != 32:  # MD5 hash is always 32 characters
        return False, "Invalid password hash format"

    return True, None


def validate_profile_input(data):
    """Validate profile creation data"""
    if not data:
        return False, "No data provided"

    company_name = data.get('company_name')
    designation = data.get('designation')

    if not company_name:
        return False, "company_name is required"

    if not designation:
        return False, "designation is required"

    return True, None


def validate_apply_input(data):
    """Validate job application data"""
    if not data:
        return False, "No data provided"

    profile_code = data.get('profile_code')

    if not profile_code:
        return False, "profile_code is required"

    try:
        int(profile_code)
    except (ValueError, TypeError):
        return False, "profile_code must be a number"

    return True, None


def validate_status_change_input(data):
    """Validate application status change data"""
    if not data:
        return False, "No data provided"

    profile_code = data.get('profile_code')
    entry_number = data.get('entry_number')
    new_status = data.get('new_status')

    if not profile_code:
        return False, "profile_code is required"

    if not entry_number:
        return False, "entry_number is required"

    if not new_status:
        return False, "new_status is required"

    valid_statuses = ['Applied', 'Not Selected', 'Selected', 'Accepted']
    if new_status not in valid_statuses:
        return False, f"new_status must be one of: {', '.join(valid_statuses)}"

    return True, None