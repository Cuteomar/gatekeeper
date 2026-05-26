"""Admin dashboard — role management, user assignment, audit logs."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import admin_required, permission_required
from app.forms import AssignRoleForm, RoleForm
from app.models import AuditLog, AuditAction, Permission, Role, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -----------------------------------------------------------------------
#  Dashboard
# -----------------------------------------------------------------------

@admin_bp.route("/")
@login_required
@admin_required
def index():
    """Admin overview — counts and recent audit events."""
    user_count     = User.query.count()
    role_count     = Role.query.count()
    recent_logs    = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    denied_count   = AuditLog.query.filter_by(action=AuditAction.ACCESS_DENIED.value).count()
    return render_template(
        "admin/index.html",
        user_count=user_count,
        role_count=role_count,
        recent_logs=recent_logs,
        denied_count=denied_count,
    )


# -----------------------------------------------------------------------
#  User management
# -----------------------------------------------------------------------

@admin_bp.route("/users")
@login_required
@permission_required(Permission.MANAGE_USERS)
def list_users():
    """List all users with their roles and active status."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/assign-role", methods=["GET", "POST"])
@login_required
@permission_required(Permission.MANAGE_USERS)
def assign_role():
    """Assign or change a user's role."""
    form = AssignRoleForm()
    # Populate choices dynamically to stay in sync with DB
    form.user_id.choices = [
        (u.id, f"{u.username} ({u.role_name})")
        for u in User.query.order_by(User.username).all()
    ]
    form.role_id.choices = [
        (r.id, r.name) for r in Role.query.order_by(Role.name).all()
    ]

    if form.validate_on_submit():
        user = db.session.get(User, form.user_id.data)
        new_role = db.session.get(Role, form.role_id.data)
        if user and new_role:
            old_role_name = user.role_name
            user.role_id = new_role.id
            db.session.commit()

            AuditLog.log(
                action=AuditAction.ROLE_CHANGE,
                user=user,
                detail=f"Role changed from '{old_role_name}' to '{new_role.name}' by admin {current_user.username}",
                ip_address=request.remote_addr,
            )
            flash(f"Assigned role '{new_role.name}' to {user.username}.", "success")
        else:
            flash("Invalid user or role selected.", "danger")
        return redirect(url_for("admin.list_users"))

    return render_template("admin/assign_role.html", form=form)


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@login_required
@permission_required(Permission.MANAGE_USERS)
def deactivate_user(user_id: int):
    """Toggle a user's active status."""
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.list_users"))

    if user.id == current_user.id:
        flash("You cannot deactivate yourself.", "danger")
        return redirect(url_for("admin.list_users"))

    user.is_active = not user.is_active
    db.session.commit()

    AuditLog.log(
        action=AuditAction.USER_DEACTIVATED,
        user=user,
        detail=f"Active status set to {user.is_active} by admin {current_user.username}",
        ip_address=request.remote_addr,
    )
    status = "activated" if user.is_active else "deactivated"
    flash(f"User '{user.username}' has been {status}.", "info")
    return redirect(url_for("admin.list_users"))


# -----------------------------------------------------------------------
#  Role management
# -----------------------------------------------------------------------

@admin_bp.route("/roles")
@login_required
@permission_required(Permission.MANAGE_ROLES)
def list_roles():
    """List all roles with their permission sets."""
    roles = Role.query.order_by(Role.name).all()
    return render_template("admin/roles.html", roles=roles)


@admin_bp.route("/roles/new", methods=["GET", "POST"])
@admin_bp.route("/roles/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required(Permission.MANAGE_ROLES)
def edit_role(role_id=None):
    """Create or edit a role and its permissions."""
    role = db.session.get(Role, role_id) if role_id else None
    form = RoleForm(obj=role)

    if form.validate_on_submit():
        if not role:
            role = Role()
            db.session.add(role)

        role.name = form.name.data
        role.description = form.description.data
        # Parse comma-separated permissions
        raw = form.permissions.data or ""
        role.permissions = {p.strip() for p in raw.split(",") if p.strip()}
        db.session.commit()

        flash(f"Role '{role.name}' saved.", "success")
        return redirect(url_for("admin.list_roles"))

    # Pre-fill permissions field for existing roles
    if role and not form.is_submitted():
        form.permissions.data = ", ".join(sorted(role.permissions))

    return render_template("admin/role_form.html", form=form, role=role)


# -----------------------------------------------------------------------
#  Audit logs
# -----------------------------------------------------------------------

@admin_bp.route("/audit-logs")
@login_required
@permission_required(Permission.VIEW_AUDIT)
def audit_logs():
    """View paginated audit log entries with optional action filter."""
    page = request.args.get("page", 1, type=int)
    action_filter = request.args.get("action", "")

    query = AuditLog.query
    if action_filter:
        query = query.filter_by(action=action_filter)

    pagination = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    logs = pagination.items
    actions = [e.value for e in AuditAction]

    return render_template(
        "admin/audit_logs.html",
        logs=logs,
        pagination=pagination,
        actions=actions,
        current_action=action_filter,
    )