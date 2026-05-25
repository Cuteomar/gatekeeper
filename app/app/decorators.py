"""Decorators for role- and permission-based access control.

Usage
-----
    @admin_required          → logged-in user must have role.name == "admin"
    @permission_required("manage:users") → user.role must include that permission
    @role_required("admin", "staff")     → user.role.name must be in the list
"""

from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user

from app.models import AuditLog, AuditAction


def admin_required(f):
    """Require the current user to have the 'admin' role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if current_user.role_name != "admin":
            _deny(f"Admin role required (user has '{current_user.role_name}')")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def permission_required(*permissions: str):
    """Require the current user to have **all** of the specified permissions.

    Accepts either the raw string (e.g. ``"manage:users"``) or a
    ``Permission`` enum member.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            missing = [p for p in permissions if not current_user.has_permission(p)]
            if missing:
                _deny(f"Missing permission(s): {', '.join(missing)}")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*roles: str):
    """Require the current user's role name to be in the provided list."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.url))
            if current_user.role_name not in roles:
                _deny(f"Required role(s): {', '.join(roles)} (user has '{current_user.role_name}')")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------

def _deny(detail):
    """Log a denied-access attempt and capture the client IP."""
    ip = request.remote_addr or "unknown"
    AuditLog.log(
        action=AuditAction.ACCESS_DENIED,
        user=current_user if current_user.is_authenticated else None,
        detail=detail,
        ip_address=ip,
    )