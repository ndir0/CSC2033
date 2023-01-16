import datetime
import re
from dateutil.relativedelta import relativedelta
from flask_wtf import FlaskForm
from models import GenderEnum
from wtforms import DateField, SelectField, StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError


SPECIAL_CHARACTERS = "*?!'^+%&/()=}][{$#@<>"


class RegisterForm(FlaskForm):
    email = StringField(validators=[Required(), Email(message="Email address is invalid.")])
    confirm_email = StringField(validators=[Required(), EqualTo("email", message="The emails do not match.")])
    password = PasswordField(
        description="Must have at least 8 characters, a letter and a number",
        validators=[Required(), Length(min=8, message="Password must have at least 8 characters.")],
    )
    confirm_password = PasswordField(
        validators=[Required(), EqualTo("password", message="The passwords do not match.")]
    )
    first_name = StringField(validators=[Required()])
    last_name = StringField(validators=[Required()])
    date_of_birth = DateField("Date of Birth", format="%Y-%m-%d", description="Must be at least 18 years old")
    gender = SelectField(choices=GenderEnum.choices())
    submit = SubmitField()

    def validate_first_name(self, first_name):
        for character in first_name.data:
            if character in SPECIAL_CHARACTERS:
                raise ValidationError("First name contains invalid characters.")

    def validate_last_name(self, last_name):
        for character in last_name.data:
            if character in SPECIAL_CHARACTERS:
                raise ValidationError("Last name contains invalid characters.")

    def validate_password(self, password):
        p = re.compile(r"(?=.*?[a-zA-Z])(?=.*\d)")
        if not p.match(password.data):
            raise ValidationError("Password must have at least a letter and a number.")

    def validate_date_of_birth(self, date_of_birth):
        if date_of_birth.data and datetime.date.today() - relativedelta(years=18) < date_of_birth.data:
            raise ValidationError("You must be at least 18 years old to register.")


class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email(message="Email address is invalid.")])
    password = PasswordField(validators=[Required()])
    submit = SubmitField()


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(validators=[Required()])
    new_password = PasswordField(
        description="Must have at least 8 characters, a letter and a number",
        validators=[Required(), Length(min=8, message="Password must have at least 8 characters.")],
    )
    confirm_new_password = PasswordField(
        validators=[Required(), EqualTo("new_password", message="The passwords do not match.")]
    )

    def validate_password(self, password):
        p = re.compile(r"(?=.*?[a-zA-Z])(?=.*\d)")
        if not p.match(password.data):
            raise ValidationError("Password must have at least a letter and a number.")


class EditForm(FlaskForm):
    email = StringField(validators=[Required(), Email(message="Email address is invalid.")])
    confirm_email = StringField(validators=[Required(), EqualTo("email", message="The emails do not match.")])
    first_name = StringField(validators=[Required()])
    last_name = StringField(validators=[Required()])
    date_of_birth = DateField("Date of Birth", format="%Y-%m-%d", description="Must be at least 18 years old")
    gender = SelectField(choices=GenderEnum.choices())
    submit = SubmitField()

    def validate_first_name(self, first_name):
        for character in first_name.data:
            if character in SPECIAL_CHARACTERS:
                raise ValidationError("First name contains invalid characters.")

    def validate_last_name(self, last_name):
        for character in last_name.data:
            if character in SPECIAL_CHARACTERS:
                raise ValidationError("Last name contains invalid characters.")

    def validate_date_of_birth(self, date_of_birth):
        if date_of_birth.data and datetime.date.today() - relativedelta(years=18) < date_of_birth.data:
            raise ValidationError("You must be at least 18 years old to register.")
