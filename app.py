# Import required libraries
import logging
import random

from functools import wraps
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy


# Filter for Health Source logging only
class HealthSourceFilter(logging.Filter):
    def filter(self, record):
        return "HS" in record.getMessage()


# Initialise formatter and file handler for logging
formatter = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler("health_source.log", "a")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.WARNING)
file_handler.addFilter(HealthSourceFilter())

# Initialise security logger
logger = logging.getLogger()
logger.propagate = False
logger.handlers.clear()
logger.addHandler(file_handler)

# Set up app configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "7h6hbjv)7n0qq1)v331@20#5&o#y$bn1go*_8j$5pv5v%o3(45"
# Development: app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///health_source.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://csc2033_team37:DumpLit9[Ado@cs-db.ncl.ac.uk/csc2033_team37"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "health.source.team37@gmail.com"
app.config["MAIL_PASSWORD"] = "cbqwvs5fxgQPchx9"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

# Initialise Bootstrap 5 form rendering
bootstrap = Bootstrap5(app)

# Initialise database
db = SQLAlchemy(app)

# Initialise mail
mail = Mail(app)

# Decorator for allowing only admins to the view
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Is the user role in the list of required roles?
        # If not, redirect to an unauthorised notice.
        if not current_user.is_admin:
            # Log unauthorised access attempt.
            logging.warning(
                "HS WARNING: Unauthorised Access Attempt [%s, %s, %s]",
                current_user.id,
                current_user.email,
                request.remote_addr,
            )
            flash("You don't have the required permissions to access that page!", "danger")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return wrapper


# Home page view
@app.route("/")
def index():
    return render_template("index.html")


# Handle common error pages
@app.errorhandler(400)
def bad_request(error):
    return render_template("400.html"), 400


@app.errorhandler(403)
def page_forbidden(error):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


@app.route("/obesity/")
def obesity():
    return render_template("obesity/about.html")


@app.route("/obesity/flashcards/")
def obesity_flashcards():
    questions1 = []
    questions2 = []
    # Import the text file containing all the questions
    with open("static/quiz/obesityQuestions.txt") as q:
        # Sort out each individual line into an array
        for i in q:
            empty = [i]
            questions1.append(empty)
    # Sort the previous array into a 2d array
    for x in questions1:
        item = x[0].split(",")
        questions2.append(item)
    # User will be able to refresh for different questions
    randomChoice = random.choice(questions2)
    question = randomChoice[0]
    answer = randomChoice[1]
    return render_template("obesity/flashcards.html", question=question, answer=answer)


@app.route("/healthy-eating/")
def healthy_eating():
    return render_template("healthy_eating/about.html")


@app.route("/healthy-eating/quiz/")
def healthy_eating_quiz():
    food1 = []
    food2 = []
    # Import the text file containing all the foods
    with open("static/quiz/foodQuestions.txt") as q:
        # Sort out each individual line into an array
        for i in q:
            empty = [i]
            food1.append(empty)
    # Sort the previous array into a 2d array
    for x in food1:
        item = x[0].split(",")
        food2.append(item)
    # User will be able to refresh for different questions
    randomChoice = random.choice(food2)
    food_name = randomChoice[0]
    calories = randomChoice[1]
    food_image = "images/food/{}.png".format(food_name).lower()
    return render_template("healthy_eating/quiz.html", food_name=food_name, food_image=food_image, calories=calories)


@app.route("/exercise")
def exercise():
    return render_template("exercise/about.html")


@app.route("/exercise/flashcards/")
def exercise_flashcards():
    questions1 = []
    questions2 = []
    # this will import the text file containing all the questions
    with open("static/quiz/exerciseQuestions.txt") as q:
        # this will sort out each individual line into an array
        for i in q:
            empty = [i]
            questions1.append(empty)
    # this will sort the previous array into a 2d array
    for x in questions1:
        item = x[0].split(",")
        questions2.append(item)
    # user will be able to refresh for different questions
    randomChoice = random.choice(questions2)
    question = randomChoice[0]
    answer = randomChoice[1]
    return render_template("exercise/flashcards.html", question=question, answer=answer)


@app.route("/subscribe/")
@login_required
def subscribe():
    from models import Newsletter

    # Check that the user is not already subscribed to the newsletter.
    newsletter = Newsletter.query.filter_by(user_id=current_user.id).first()
    if newsletter:
        flash("You are already subscribed to the newsletter!", "warning")
        return redirect(url_for("index"))

    # Create a newsletter subscription with the current user's email.
    new_newsletter = Newsletter(user_id=current_user.id)

    # Add the newsletter subscription to the database and save.
    db.session.add(new_newsletter)
    db.session.commit()

    # Log newsletter subscription.
    logging.warning(
        "HS INFO: Newsletter Subscribed [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr
    )

    # Redirect the user to the home page.
    flash("You have successfully subscribed to the newsletter", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    login_manager = LoginManager()
    login_manager.login_view = "users.login"
    login_manager.login_message = "You need to log in before accessing that page!"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from users.views import users_blueprint
    from recipes.views import recipes_blueprint
    from calories.views import calories_blueprint
    from admin.views import admin_blueprint

    app.register_blueprint(users_blueprint)
    app.register_blueprint(recipes_blueprint)
    app.register_blueprint(calories_blueprint)
    app.register_blueprint(admin_blueprint)
    app.run()
