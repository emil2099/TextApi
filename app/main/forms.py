from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import audios


class TextInput(FlaskForm):
    text = StringField('Enter text to classify', validators=[DataRequired()])
    submit = SubmitField('Find themes')

class AudioUpload(FlaskForm):
    title = StringField('Title', validators=[DataRequired])
    description = StringField('Description', validators=[DataRequired])
    audio = FileField('Audio file', validators=[FileRequired(), FileAllowed(audios, 'WAV files only!')])
