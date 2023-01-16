import datetime
import logging
import random
from app import db
from dateutil.relativedelta import relativedelta
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc
from models import ProgressEntry
from calories.forms import ProgressForm
from calories.utils import calculateBMI, calculateBMR


calories_blueprint = Blueprint("calories", __name__, template_folder="templates")


# About Calories View
@calories_blueprint.route("/calories/", methods=["GET"])
def about():
    # Is the user authenticated?
    if current_user.is_authenticated:
        entry = ProgressEntry.query.filter_by(user_id=current_user.id).order_by(desc("created_on")).first()

        # Did they track some progress?
        if entry:
            bmr = calculateBMR(
                height=entry.height,
                weight=entry.weight,
                age=relativedelta(datetime.date.today(), current_user.date_of_birth).years,
                level_of_activity=entry.level_of_activity,
                gender=current_user.gender,
            )
            return render_template("calories/about.html", bmr=bmr)

    # The user tracked no progress or is not authenticated. Do not calculate the BMR.
    return render_template("calories/about.html")


# Calories Flashcards View
@calories_blueprint.route("/calories/flashcards/", methods=["GET"])
def flashcards():
    questions1 = []
    questions2 = []
    # Import the text file containing all the questions
    with open("static/quiz/caloriesQuestions.txt") as q:
        # Sort out each individual line into an array
        for i in q:
            empty = [i]
            questions1.append(empty)
    # sort the previous array into a 2d array
    for x in questions1:
        item = x[0].split(",")
        questions2.append(item)
    # User will be able to refresh for different questions
    randomChoice = random.choice(questions2)
    question = randomChoice[0]
    answer = randomChoice[1]
    return render_template("calories/flashcards.html", question=question, answer=answer)


@calories_blueprint.route("/progress/", methods=["GET"])
def view_progress():
    # Is the user authenticated?
    if current_user.is_authenticated:
        entries = ProgressEntry.query.filter_by(user_id=current_user.id).order_by(desc("created_on")).all()

        # Did they track some progress?
        if entries:
            last_entry = entries[0]
            bmi = calculateBMI(height=last_entry.height, weight=last_entry.weight)
            bmr = calculateBMR(
                height=last_entry.height,
                weight=last_entry.weight,
                age=relativedelta(datetime.date.today(), current_user.date_of_birth).years,
                level_of_activity=last_entry.level_of_activity,
                gender=current_user.gender,
            )

            # Calculate BMI status.
            if bmi < 16.5:
                bmi_status = ("danger", "very underweight")
            elif bmi < 18.5:
                bmi_status = ("warning", "underweight")
            elif bmi < 25:
                bmi_status = ("success", "in the normal range")
            elif bmi < 30:
                bmi_status = ("warning", "overweight")
            else:
                bmi_status = ("danger", "obese")

            return render_template(
                "calories/progress/view.html", entries=entries, bmi=bmi, bmr=bmr, bmi_status=bmi_status
            )

    # The user tracked no progress or is not authenticated. Do not calculate the BMI or BMR.
    return render_template("calories/progress/view.html")


@calories_blueprint.route("/progress/add/", methods=["GET", "POST"])
@login_required
def add_progress():
    form = ProgressForm()

    # Is this a POST request and is the form valid?
    if form.validate_on_submit():
        # Add a new progress entry with the form data.
        new_progress_entry = ProgressEntry(
            user_id=current_user.id,
            height=form.height.data,
            weight=form.weight.data,
            level_of_activity=form.level_of_activity.data,
        )

        # Add the new progress entry to the database and save.
        db.session.add(new_progress_entry)
        db.session.commit()

        # Log recipe creation.
        logging.warning(
            "HS INFO: Progress Entry Added [%s, %s, %s, %s]",
            new_progress_entry.id,
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the recipes list page.
        flash("The progress entry has been successfully added.", "success")
        return redirect(url_for("calories.view_progress"))

    # This is a GET request or the form is invalid.
    return render_template("calories/progress/add.html", form=form)


@calories_blueprint.route("/progress/<int:id>/delete/", methods=["GET", "POST"])
@login_required
def delete_progress(id=None):
    # Check that the progress entry exists.
    entry = ProgressEntry.query.filter_by(id=id).first()
    if not entry:
        flash("The progress entry doesn't exist!", "danger")
        return redirect(url_for("calories.view_progress"))

    # Check that user has the permissions to delete the progress entry.
    if not (entry.user_id == current_user.id or current_user.is_admin):
        flash("You don't have the permissions to access that page!", "danger")
        return redirect(url_for("recipes.list"))

    if request.method == "POST":
        ProgressEntry.query.filter_by(id=entry.id).delete()
        db.session.commit()

        # Redirect the user to the progress tracking page.
        flash("You have successfully deleted the progress entry.", "success")
        return redirect(url_for("calories.view_progress"))

    # This is a GET request.
    return render_template("calories/progress/delete.html", entry=entry)
