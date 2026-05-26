"""WTForms definitions for login, registration, and role management."""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, TextAreaField,
    BooleanField, SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, Optional

from app.models import Role


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Log In")


class RegisterForm(FlaskForm):
    username = StringField("Username",   validators=[DataRequired(), Length(3, 80)])
    email    = StringField("Email",      validators=[DataRequired(), Email(), Length(1, 120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 128)])
    submit   = SubmitField("Register")

    def role_choices():
        return [(str(r.id), r.name) for r in Role.query.all()] or [("", "No roles available")]


class RoleForm(FlaskForm):
    name        = StringField("Role Name", validators=[DataRequired(), Length(1, 64)])
    description = StringField("Description", validators=[Optional(), Length(0, 255)])
    permissions = TextAreaField(
        "Permissions (comma-separated)",
        validators=[Optional()],
        description="e.g. read:content, write:content, manage:users"
    )
    submit = SubmitField("Save Role")


class AssignRoleForm(FlaskForm):
    user_id = SelectField("User", coerce=int, validators=[DataRequired()])
    role_id = SelectField("Role", coerce=int, validators=[DataRequired()])
    submit  = SubmitField("Assign Role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id.choices = [
            (u.id, f"{u.username} ({u.role_name})")
            for u in __import__("app.models", fromlist=["User"]).User.query.order_by("username").all()
        ]
        self.role_id.choices = [
            (r.id, r.name) for r in Role.query.order_by("name").all()
        ]