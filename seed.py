"""Seed script — creates default roles and sample users.

Usage
-----
    python seed.py          # Standalone
    from seed import seed_database  # Called by app factory on empty DB
"""

from app import create_app, db
from app.models import Role, User, Permission


def seed_database():
    """Create default roles and users if they don't exist."""
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
            print("  ✓ Created role: {}".format(name))
        else:
            print("  - Skipped role '{}' (already exists)".format(name))

    db.session.commit()

    users_data = [
        ("admin", "admin@example.com", "admin123", "admin"),
        ("staff", "staff@example.com", "staff123", "staff"),
        ("guest", "guest@example.com", "guest123", "guest"),
    ]

    for username, email, password, role_name in users_data:
        if not User.query.filter_by(username=username).first():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user = User(username=username, email=email, role_id=role.id, is_active=True)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                print("  ✓ Created {} user: {} / {}".format(role_name, username, password))
            else:
                print("  - Skipped {}: role '{}' not found".format(username, role_name))
        else:
            print("  - Skipped user '{}' (already exists)".format(username))

    print("\nSeed complete.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
        print("You can now run: flask run")