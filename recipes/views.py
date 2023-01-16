import logging
from app import db
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from models import Recipe, User
from recipes.forms import RecipeForm


recipes_blueprint = Blueprint("recipes", __name__, template_folder="templates")


# List Recipes View
@recipes_blueprint.route("/recipes/", methods=["GET"])
def list():
    # Are we receving a search query?
    # If so, search for similar recipe names and order them by most recent.
    search_query = request.args.get("search")
    if search_query:
        recipes = Recipe.query.filter(Recipe.name.like("%" + search_query + "%")).order_by(desc("created_on")).all()
    else:
        recipes = Recipe.query.order_by(desc("created_on")).all()

    for recipe in recipes:
        user = User.query.filter_by(id=recipe.user_id).first()
        recipe.user_name = user.full_name

    return render_template("recipes/list.html", recipes=recipes)


# View Recipe View
@recipes_blueprint.route("/recipes/<int:id>/", methods=["GET"])
def view(id):
    # Check that the recipe exists
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        flash("The recipe doesn't exist!", "danger")
        return redirect(url_for("recipes.list"))

    # Get the recipe's creator.
    creator = User.query.filter_by(id=recipe.user_id).first()

    return render_template("recipes/view.html", recipe=recipe, creator=creator)


# Create Recipe View
@recipes_blueprint.route("/recipes/create/", methods=["GET", "POST"])
@login_required
def create():
    form = RecipeForm()

    # Is this a POST request and is the form valid?
    if form.validate_on_submit():
        # Create a new recipe with the form data.
        new_recipe = Recipe(
            user_id=current_user.id,
            name=form.name.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbohydrate=form.carbohydrate.data,
            fat=form.fat.data,
            body=form.body.data,
        )

        # Add the new recipe to the database and save.
        db.session.add(new_recipe)
        db.session.commit()

        # Log recipe creation.
        logging.warning(
            "HS INFO: Recipe Created [%s, %s, %s, %s]",
            new_recipe.id,
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the recipes list page.
        flash("The recipe has been successfully created.", "success")
        return redirect(url_for("recipes.view", id=new_recipe.id))

    # This is a GET request or the form is invalid.
    return render_template("recipes/create.html", form=form)


# Edit Recipe View
@recipes_blueprint.route("/recipes/<int:id>/edit/", methods=["GET", "POST"])
@login_required
def edit(id):
    # Check that the recipe exists.
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        flash("The recipe doesn't exist!", "danger")
        return redirect(url_for("recipes.list"))

    # Check that user has the permissions to edit the recipe.
    if not (recipe.user_id == current_user.id or current_user.is_admin):
        flash("You don't have the permissions to access that page!", "danger")
        return redirect(url_for("recipes.list"))

    # Initialise the form with data from the recipe.
    form = RecipeForm(obj=recipe)

    # Is this a POST request and is the form valid?
    if form.validate_on_submit():
        # Update the recipe with the new data and save to the database.
        form.populate_obj(recipe)
        db.session.commit()

        # Log recipe editing.
        logging.warning(
            "HS INFO: Recipe Edited [%s, %s, %s, %s]",
            recipe.id,
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the recipes page.
        flash("The recipe has been successfully edited.", "success")
        return redirect(url_for("recipes.view", id=recipe.id))

    # This is a GET request or the form is invalid.
    return render_template("recipes/edit.html", form=form)


# Delete Recipe View
@recipes_blueprint.route("/recipes/<int:id>/delete/", methods=["GET", "POST"])
@login_required
def delete(id):
    # Check that the recipe exists.
    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        flash("The recipe doesn't exist!", "danger")
        return redirect(url_for("recipes.list"))

    # Check that user has the permissions to delete the recipe.
    if not (recipe.user_id == current_user.id or current_user.is_admin):
        flash("You don't have the permissions to access that page!", "danger")
        return redirect(url_for("recipes.list"))

    # Is this a POST request?
    if request.method == "POST":
        # Delete the recipe and save to the database.
        Recipe.query.filter_by(id=id).delete()
        db.session.commit()

        # Log recipe deletion.
        logging.warning(
            "HS INFO: Recipe Deleted [%s, %s, %s, %s]",
            recipe.id,
            current_user.id,
            current_user.email,
            request.remote_addr,
        )

        # Redirect the user to the recipes page.
        flash("You have successfully deleted the recipe.", "success")
        return redirect(url_for("recipes.list"))

    # This is a GET request.
    return render_template("recipes/delete.html", recipe=recipe)
