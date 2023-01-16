import enum
import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash


class GenderEnum(enum.Enum):
    MALE = "m"
    FEMALE = "f"

    @classmethod
    def choices(cls):
        return [(member.value, name.capitalize()) for name, member in cls.__members__.items()]


class User(db.Model, UserMixin):
    """This model represents a user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Authentication information
    email = db.Column(db.String(255), nullable=False, unique=True)
    _password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # User information
    first_name = db.Column(db.String(35), nullable=False)
    last_name = db.Column(db.String(35), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(GenderEnum, values_callable=lambda x: [c.value for c in GenderEnum]), nullable=False)

    # Log information
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, password, first_name, last_name, date_of_birth, gender, is_admin=False):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.is_admin = is_admin

    @hybrid_property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def password(self):
        """Return the hashed user's password."""
        return self._password

    @password.setter
    def password(self, password):
        """Hash the user's password before writing to the database."""
        self._password = generate_password_hash(password)


class Newsletter(db.Model):
    """This model represents an email registration for the newsletter."""

    __tablename__ = "newsletters"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), unique=True)

    # Log information
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, user_id):
        self.user_id = user_id

    @hybrid_property
    def email(self):
        """Return the subscriber's email."""
        return User.query.filter_by(id=self.user_id).first().email


class Recipe(db.Model):
    """This model represents a recipe."""

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # Recipe information
    name = db.Column(db.Text, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    carbohydrate = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    body = db.Column(db.Text, nullable=False)

    # Log information
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, user_id, name, calories, fat, carbohydrate, protein, body):
        self.user_id = user_id
        self.name = name
        self.calories = calories
        self.fat = fat
        self.carbohydrate = carbohydrate
        self.protein = protein
        self.body = body


class ProgressEntry(db.Model):
    """This model represents a progress entry at a specific point in time."""

    __tablename__ = "progress_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # Progress information
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.FLOAT, nullable=False)
    level_of_activity = db.Column(db.Integer, nullable=False)

    # Log information
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, user_id, height, weight, level_of_activity):
        self.user_id = user_id
        self.height = height
        self.weight = weight
        self.level_of_activity = level_of_activity


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


def add_test_data():
    admin = User(
        email="admin@email.com",
        password="admin1!",
        first_name="Admin",
        last_name="Account",
        date_of_birth=datetime.date.today() - datetime.timedelta(days=10000),
        gender="m",
        is_admin=True,
    )
    db.session.add(admin)
    user = User(
        email="user@email.com",
        password="user1!",
        first_name="User",
        last_name="Account",
        date_of_birth=datetime.date.today() - datetime.timedelta(days=10000),
        gender="m",
        is_admin=False,
    )
    db.session.add(user)
    db.session.commit()
