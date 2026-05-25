"""Database models for the RBAC system.

User      — Stores credentials, active status, and a role FK.
Role      — Defines a named role with a set of permissions.
AuditLog  — Records authentication and authorisation events.
"""

import enum
from datetime import datetime, timezone

from flask_login import UserMixin

from app import db, bcrypt, login_manager


# ---------------------------------------------------------------------------
#  Enum helpers
# ---------------------------------------------------------------------------

class Permission(str, enum.Enum):
    """Granular permissions that can be assigned to a role."""
    READ_CONTENT   = "read:content"
    WRITE_CONTENT  = "write:content"
    MANAGE_USERS   = "manage:users"
    MANAGE_ROLES   = "manage:roles"
    VIEW_AUDIT     = "view:audit"
    EXPORT_DATA    = "export:data"


class AuditAction(str, enum.Enum):
    LOGIN_SUCCESS       = "login_success"
    LOGIN_FAILURE       = "login_failure"
    LOGOUT              = "logout"
    ROLE_CHANGE         = "role_change"
    ACCESS_DENIED       = "access_denied"
    USER_CREATED        = "user_created"
    USER_DEACTIVATED    = "user_deactivated"


# ---------------------------------------------------------------------------
#  Role
# ---------------------------------------------------------------------------

class Role(db.Model):
    __tablename__ = "roles"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), default="")
    _permissions = db.Column("permissions", db.Text, default="")

    users = db.relationship("User", backref="role", lazy="dynamic")

    @property
    def permissions(self):
        return set(p.strip() for p in self._permissions.split(",") if p.strip())

    @permissions.setter
    def permissions(self, value):
        self._permissions = ",".join(sorted(value))

    def has_permission(self, perm):
        if isinstance(perm, Permission):
            return perm.value in self.permissions
        return perm in self.permissions

    def __repr__(self):
        return "<Role {}>".format(self.name)


# ---------------------------------------------------------------------------
#  User
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email        = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active    = db.Column(db.Boolean, default=True, nullable=False)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    role_id      = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=True)

    def set_password(self, plaintext):
        self.password_hash = bcrypt.generate_password_hash(plaintext).decode("utf-8")

    def check_password(self, plaintext):
        return bcrypt.check_password_hash(self.password_hash, plaintext)

    @property
    def role_name(self):
        return self.role.name if self.role else "unassigned"

    def has_permission(self, perm):
        return bool(self.role and self.role.has_permission(perm))

    # Flask-Login interface
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return "<User {} ({})>".format(self.username, self.role_name)


# ---------------------------------------------------------------------------
#  Audit log
# ---------------------------------------------------------------------------

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    username    = db.Column(db.String(80), nullable=True)
    action      = db.Column(db.String(32), nullable=False)
    detail      = db.Column(db.Text, default="")
    ip_address  = db.Column(db.String(45), nullable=True)

    user = db.relationship("User", backref="audit_logs")

    @classmethod
    def log(cls, action, user=None, detail="", ip_address=None):
        entry = cls(
            action    = action.value if isinstance(action, AuditAction) else action,
            user_id   = user.id if user else None,
            username  = user.username if user else "anonymous",
            detail    = detail,
            ip_address= ip_address,
        )
        db.session.add(entry)
        db.session.commit()

    def __repr__(self):
        return "<AuditLog {} by {} at {}>".format(self.action, self.username, self.timestamp)


# ---------------------------------------------------------------------------
#  Load user for Flask-Login
# ---------------------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))