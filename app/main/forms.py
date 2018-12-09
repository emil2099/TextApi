from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import audios
from flask import flash


class TextInput(FlaskForm):
    text = StringField('Enter text to classify', validators=[DataRequired()])
    submit = SubmitField('Find themes')


class AudioUpload(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    audio_file = FileField('Audio file', validators=[FileRequired(), FileAllowed(audios, 'WAV files only!')])
    # audio_file = FileField('Audio file', validators=[FileRequired(), FileAllowed(audios, 'WAV files only!')])
    submit = SubmitField('Upload WAV')


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))