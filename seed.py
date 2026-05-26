#!/usr/bin/env python3
"""Seed script — creates the default roles (admin, staff, guest) and an
admin user so the application is usable immediately.

Usage
-----
    python seed.py
"""

from app import create_app, db
from app.models import Role, User, Permission

app = create_app()

with app.app_context():
    db.create_all()

    # ------------------------------------------------------------------ #
    #  1. Create default roles
    # ------------------------------------------------------------------ #
    roles_data = {
        "admin": {
            "description": "Full system access — manage users, roles, and audit logs.",
            "permissions": {
                Permission.READ_CONTENT,
                Permission.WRITE_CONTENT,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_AUDIT,
                Permission.EXPORT_DATA,
            },
        },
        "staff": {
            "description": "Can read and write content; access the staff area.",
            "permissions": {
                Permission.READ_CONTENT,
                Permission.WRITE_CONTENT,
            },
        },
        "guest": {
            "description": "Read-only access to public content.",
            "permissions": {
                Permission.READ_CONTENT,
            },
        },
    }

    for name, data in roles_data.items():
        existing = Role.query.filter_by(name=name).first()
        if not existing:
            role = Role(name=name, description=data["description"])
            role.permissions = data["permissions"]
            db.session.add(role)
            print(f"  ✓ Created role: {name}")
        else:
            print(f"  - Skipped role '{name}' (already exists)")

    db.session.commit()

    # ------------------------------------------------------------------ #
    #  2. Create default admin user (password: admin123)
    # ------------------------------------------------------------------ #
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role and not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            email="admin@example.com",
            role_id=admin_role.id,
            is_active=True,
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()
        print("  ✓ Created admin user: admin / admin123")
    else:
        print("  - Skipped admin user (already exists or admin role missing)")

    # ------------------------------------------------------------------ #
    #  3. Create a sample staff user (password: staff123)
    # ------------------------------------------------------------------ #
    staff_role = Role.query.filter_by(name="staff").first()
    if staff_role and not User.query.filter_by(username="staff").first():
        staff_user = User(
            username="staff",
            email="staff@example.com",
            role_id=staff_role.id,
            is_active=True,
        )
        staff_user.set_password("staff123")
        db.session.add(staff_user)
        db.session.commit()
        print("  ✓ Created staff user: staff / staff123")
    else:
        print("  - Skipped staff user (already exists or staff role missing)")

    # ------------------------------------------------------------------ #
    #  4. Create a sample guest user (password: guest123)
    # ------------------------------------------------------------------ #
    guest_role = Role.query.filter_by(name="guest").first()
    if guest_role and not User.query.filter_by(username="guest").first():
        guest_user = User(
            username="guest",
            email="guest@example.com",
            role_id=guest_role.id,
            is_active=True,
        )
        guest_user.set_password("guest123")
        db.session.add(guest_user)
        db.session.commit()
        print("  ✓ Created guest user: guest / guest123")
    else:
        print("  - Skipped guest user (already exists or guest role missing)")

    print("\nSeed complete. You can now run: flask run")