"""
API Routes Package
Contains all route blueprints for the application
"""

from .auth import auth_bp
from .student import student_bp
from .recruiter import recruiter_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'student_bp', 'recruiter_bp', 'admin_bp']