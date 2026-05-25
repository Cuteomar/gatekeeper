"""Authentication routes — login, logout, registration."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import LoginForm, RegisterForm
from app.models import AuditLog, AuditAction, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user by username and password (bcrypt-verified)."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("This account has been deactivated.", "danger")
                return render_template("login.html", form=form)

            login_user(user, remember=True)
            AuditLog.log(
                action=AuditAction.LOGIN_SUCCESS,
                user=user,
                detail=f"Login from {request.remote_addr}",
                ip_address=request.remote_addr,
            )
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for("main.dashboard"))

        # Failed login
        AuditLog.log(
            action=AuditAction.LOGIN_FAILURE,
            user=None,
            detail=f"Failed login attempt for username='{form.username.data}'",
            ip_address=request.remote_addr,
        )
        flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "danger")
            return render_template("register.html", form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        AuditLog.log(
            action=AuditAction.USER_CREATED,
            user=user,
            detail="User self-registered",
            ip_address=request.remote_addr,
        )
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user and record the event."""
    AuditLog.log(
        action=AuditAction.LOGOUT,
        user=current_user,
        detail="User logged out",
        ip_address=request.remote_addr,
    )
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))