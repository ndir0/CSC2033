from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, FloatField
from wtforms.validators import ValidationError


class ProgressForm(FlaskForm):
    height = IntegerField("Height (in)")
    weight = FloatField("Weight (lbs)")
    level_of_activity = IntegerField("Level of Activity")
    submit = SubmitField()

    def validate_level_of_activity(self, level_of_activity):
        if level_of_activity.data not in [1, 2, 3]:
            raise ValidationError("Must be either 1, 2 or 3")
