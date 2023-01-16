from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, SubmitField, TextAreaField
from wtforms.validators import Length, Required


class RecipeForm(FlaskForm):
    name = StringField(validators=[Length(max=50), Required()])
    calories = IntegerField("Calories (kcal)")
    fat = FloatField("Fat (g)")
    carbohydrate = FloatField("Carbohydrate (g)")
    protein = FloatField("Protein (g)")
    body = TextAreaField(validators=[Required()])
    submit = SubmitField()
