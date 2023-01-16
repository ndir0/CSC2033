import datetime
import logging
from app import admin_required, db
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from users.forms import RegisterForm, LoginForm, PasswordChangeForm, EditForm
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash
from models import User


users_blueprint = Blueprint("users", __name__, template_folder="templates")


# Register View
@users_blueprint.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You cannot register an account while being logged in!", "warning")
        return redirect(url_for("users.profile"))

    form = RegisterForm()

    # Is this a POST request or is the form valid?
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Does a user with that email already exist?
        # If so, return to the register page.
        if user:
            flash("The email address is already in use!", "form")
            return render_template("users/register.html", form=form)

        # Create a new user with the form data.
        new_user = User(
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
        )

        # Add the new user to the database and save.
        db.session.add(new_user)
        db.session.commit()

        # Log registration.
        logging.warning("HS INFO: User Registration [%s, %s, %s]", new_user.id, new_user.email, request.remote_addr)

        # Redirect the user to the login page.
        flash(f"Welcome to Health Source, {form.first_name.data}! You have successfully registered.", "success")
        return redirect(url_for("users.login"))

    # This is a GET request or the form is invalid.
    return render_template("users/register.html", form=form)


# Login View
@users_blueprint.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "warning")
        return redirect(url_for("users.profile"))

    form = LoginForm()

    # Is this a POST request or is the form valid?
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Is the email and password combination correct?
        # If not, return to the login page and show an error message.
        if not user or not check_password_hash(user.password, form.password.data):
            # Log incorrect login attempt.
            logging.warning("HS WARNING: Failed Login Attempt [%s, %s]", form.email.data, request.remote_addr)

            flash("The email and/or password you have entered is incorrect!", "form")
            return render_template("users/login.html", form=form)

        login_user(user)

        # Set the date and time of the last login.
        user.last_login = datetime.datetime.now()

        # Save the changes to the database.
        db.session.commit()

        # Log login.
        logging.warning("HS INFO: User Login [%s, %s, %s]", user.id, user.email, request.remote_addr)

        # Do we have next parameter?
        # If so, redirect there instead of the profile page.
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("users.profile")

        # Redirect the user to the next page.
        flash(f"Welcome back, {user.first_name}! You have sucessfully logged in.", "success")
        return redirect(next_page)

    # This is a GET request or the form is invalid. Return to the login page.
    return render_template("users/login.html", form=form)


# Logout View
@users_blueprint.route("/logout/", methods=["GET"])
def logout():
    if not current_user.is_authenticated:
        flash("You are already logged out!", "warning")
        return redirect(url_for("index"))

    # Log logout.
    logging.warning("HS INFO: User Logout [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr)

    logout_user()

    # Redirect the user to the home page after logging them out.
    flash("You have sucessfully logged out.", "success")
    return redirect(url_for("index"))


# Profile View
@users_blueprint.route("/profile/", methods=["GET"])
@users_blueprint.route("/profile/<int:id>/", methods=["GET"])
@login_required
def profile(id=None):
    # Is there an no ID passed by the URL?
    # If so, show the current user's profile page.
    if not id:
        return render_template("users/profile.html", account=current_user)
    # There is an ID passed by the URL. Is it the current user's ID or is the current user an admin?
    elif current_user.id == id or current_user.is_admin:
        return render_template("users/profile.html", account=User.query.filter_by(id=id).first())
    # None of the above apply. The user cannot access this page.
    else:
        flash("You don't have the required permissions to access that page!", "danger")
        return redirect(url_for("index"))


# Change Password View
@users_blueprint.route("/change-password/", methods=["GET", "POST"])
@login_required
def change_password():
    form = PasswordChangeForm()

    # Is this a POST request or is the form valid?
    if form.validate_on_submit():
        # Is the current password correct?
        # If not, return to the change password page and show an error message.
        if not check_password_hash(current_user.password, form.current_password.data):
            # Log incorrect attempt.
            logging.warning(
                "HS WARNING: Failed User Password Change Attempt [%s, %s, %s]",
                current_user.id,
                current_user.email,
                request.remote_addr,
            )

            flash("The current password is incorrect!", "form")
            return render_template("users/change_password.html", form=form)

        # Set the new password and save to the database.
        current_user.password = form.new_password.data
        db.session.commit()

        # Log password change.
        logging.warning(
            "HS INFO: User Password Change [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr
        )

        # Log out user and redirect them to the login page.
        logout_user()
        flash("You have successfully changed your password.", "success")
        return redirect(url_for("users.login"))

    # This is a GET request or the form is invalid. Go to the password change page.
    return render_template("users/change_password.html", form=form)


# Change Permissions View
@users_blueprint.route("/change-permissions/<int:id>/", methods=["GET", "POST"])
@login_required
@admin_required
def change_permissions(id):
    # Check that the account exists.
    account = User.query.filter_by(id=id).first()
    if not account:
        flash("The account doesn't exist!", "danger")
        return redirect(url_for("users.list"))

    # Figure out the new role for the user.
    if account.is_admin:
        new_role = "a normal user"
    else:
        new_role = "an admin"

    # Is this a POST request?
    if request.method == "POST":
        # Reverse the admin status of the user and save to the database.
        account.is_admin = not account.is_admin
        db.session.commit()

        # Log action.
        logging.warning(
            "HS WARNING: Account Made [%s, %s, %s, %s]",
            new_role,
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the home page if they deleted their own account.
        # Otherwise, send them to the list view.
        flash(f"You have successfully made {account.full_name} {new_role}.", "success")
        return redirect(url_for("users.profile", id=id))

    # This is a GET request or the form is invalid.
    return render_template("users/change_permissions.html", account=account, new_role=new_role)


# List Accounts View
@users_blueprint.route("/accounts/", methods=["GET"])
@login_required
@admin_required
def list():
    # Are we receving a search query?
    # If so, search for similar user names and order them by last name.
    search_query = request.args.get("search")
    if search_query:
        accounts = (
            User.query.filter((User.first_name + " " + User.last_name).like("%" + search_query + "%"))
            .order_by("last_name")
            .all()
        )
    else:
        accounts = User.query.order_by("last_name").all()

    return render_template("users/list.html", accounts=accounts)


# Edit Account View
@users_blueprint.route("/accounts/<int:id>/edit/", methods=["GET", "POST"])
@login_required
def edit(id):
    # Is it the current user's ID or is the current user an admin?
    if current_user.id == id or current_user.is_admin:
        account = User.query.filter_by(id=id).first()
    # It is neither. The user cannot access this page.
    else:
        flash("You don't have the required permissions to access that page!", "danger")
        return redirect(url_for("index"))

    form = EditForm(obj=account, confirm_email=account.email)

    # Is this a POST request or is the form valid?
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Does a user with that email already exist and it is not the current user?
        # If so, return to the register page.
        if user and user.id != account.id:
            flash("The email address is already in use!", "form")
            return render_template("users/edit.html", form=form)

        # Update the recipe with the new data and save to the database.
        form.populate_obj(account)
        db.session.commit()

        # Log account editing.
        logging.warning(
            "HS INFO: Account Edited [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr
        )

        # Redirect the user to the profile page.
        flash("You have successfully edited the account.", "success")
        return redirect(url_for("users.profile"))

    # This is a GET request or the form is invalid. Go to the edit account page.
    return render_template("users/edit.html", form=form)


# Delete View
@users_blueprint.route("/accounts/<int:id>/delete/", methods=["GET", "POST"])
@login_required
def delete(id):
    # Is it the current user's ID or is the current user an admin?
    if current_user.id == id or current_user.is_admin:
        account = User.query.filter_by(id=id).first()
    # It is neither. The user cannot access this page.
    else:
        flash("You don't have the required permissions to access that page!", "danger")
        return redirect(url_for("index"))

    # Is this a POST request?
    if request.method == "POST":
        # Delete the account and save to the database.
        User.query.filter_by(id=account.id).delete()
        db.session.commit()

        # Log account deletion.
        logging.warning(
            "HS WARNING: Account Deleted [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr
        )

        # Log out and redirect the user to the home page if they deleted their own account.
        # Otherwise, send them to the list view.
        if current_user.id == account.id:
            next_page = url_for("index")
            logout_user()
        else:
            next_page = url_for("users.list")

        # Redirect the user to the next view.
        flash("You have successfully deleted the account.", "success")
        return redirect(next_page)

    # This is a GET request or the form is invalid.
    return render_template("users/delete.html")
