from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TextInput(FlaskForm):
    text = StringField('Enter text to classify', validators=[DataRequired()])
    submit = SubmitField('Find themes')