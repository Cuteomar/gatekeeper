"""Public / main routes — dashboard and general pages."""

from flask import Blueprint, render_template
from flask_login import login_required

from app.decorators import role_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard — content varies by role.

    The template renders sections based on **role.name**, but the
    real authorisation gate is at the endpoint level via decorators.
    """
    return render_template("dashboard.html")


@main_bp.route("/staff-area")
@login_required
@role_required("admin", "staff")
def staff_area():
    """Area restricted to staff and admin roles."""
    return render_template("staff_area.html")