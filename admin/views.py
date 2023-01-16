import logging
from app import admin_required, db, mail
from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from flask_mail import Message
from admin.forms import NewsletterForm
from models import Newsletter


admin_blueprint = Blueprint("admin", __name__, template_folder="templates")


# List Logs View
@admin_blueprint.route("/admin/logs/", methods=["GET"])
@login_required
@admin_required
def list_logs():
    # Read the logs from the file and display them in reverse order.
    with open("health_source.log", "r") as f:
        logs = f.read().splitlines()
        logs.reverse()

    return render_template("admin/logs/list.html", logs=logs)


# Clear Logs View
@admin_blueprint.route("/admin/logs/clear/", methods=["GET", "POST"])
@login_required
@admin_required
def clear_logs():
    # Is this a POST request?
    if request.method == "POST":
        # Clear the logs file.
        open("health_source.log", "w").close()

        # Log it.
        logging.warning(
            "HS WARNING: Logs Cleared [%s, %s, %s]", current_user.id, current_user.email, request.remote_addr
        )

        # Redirect to the logs page after clearing the logs.
        flash("You have successfully cleared the log file.", "success")
        return redirect(url_for("admin.list_logs"))

    # This is a GET request. Display the "Clear Logs" template.
    return render_template("admin/logs/clear.html")


# Send Newsletter View
@admin_blueprint.route("/admin/newsletters/send/", methods=["GET", "POST"])
@login_required
@admin_required
def send_newsletter():
    form = NewsletterForm()

    # Get all the newsletter subscribers' email
    subscriber_emails = [subscriber.email for subscriber in Newsletter.query.all()]

    # Is this a POST request and is the form valid?
    if form.validate_on_submit():
        # Message every subscriber.
        for subscriber_email in subscriber_emails:
            # Initialise the message with form data and get the user's email from the newsletter.
            # Then, send the message.
            message = Message(
                subject=form.subject.data,
                body=form.body.data,
                sender="health.source.team37@gmail.com",
                recipients=[subscriber_email],
            )
            mail.send(message)

        # Log newsletter sending.
        logging.warning(
            "HS INFO: Newsletter Sent [%s, %s, %s, %s]",
            len(subscriber_emails),
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the home page.
        flash("The newsletter has been successfully sent.", "success")
        return redirect(url_for("index"))

    # This is a GET request or the form is invalid.
    return render_template("admin/newsletters/send.html", form=form, subscriber_emails=subscriber_emails)
