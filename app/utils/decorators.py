from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def _check_permission(required_permissions):
    """Helper function to check user permissions."""
    verify_jwt_in_request()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.permission_type not in required_permissions:
        return (
            jsonify(message="Forbidden: You do not have the necessary permissions."),
            403,
        )
    return None


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        permission_error = _check_permission(["admin", "super_admin"])
        if permission_error:
            return permission_error
        return fn(*args, **kwargs)

    return wrapper


def super_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        permission_error = _check_permission(["super_admin"])
        if permission_error:
            return permission_error
        return fn(*args, **kwargs)

    return wrapper
