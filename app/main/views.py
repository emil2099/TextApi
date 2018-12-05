from flask import render_template, redirect, url_for, request, current_app, session

from app import db
from app.main import main
from app.main.forms import TextInput
from app.models import Text

from app import speech_client, speech_config, types
import io
import sys


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/classify', methods=['GET', 'POST'])
def classify_text():
    # text = None
    form = TextInput()
    if form.validate_on_submit():
        text = Text(text=form.text.data)
        text.classify_themes()
        db.session.add(text)
        db.session.commit()
        session['text_id'] = text.id
        # session['text'] = form.text.data
        # session['sentences'] = classifier.predict(session['text'])
        return redirect(url_for('main.classify_text'))
    text = Text.query.filter_by(id=session.pop('text_id', None)).first()
    # text = session.pop('text', None)
    # sentences = session.pop('sentences', [])
    return render_template('classify.html', form=form, text=text)


@main.route('/history')
def classification_history():
    page = request.args.get('page', type=int)
    pagination = Text.query.order_by(Text.timestamp.desc()).paginate(
        page, per_page=current_app.config['TEXTS_PER_PAGE'], error_out=False)
    texts = pagination.items
    return render_template('history.html', texts=texts, pagination=pagination)


@main.route('/speech')
def speech_recognition():
    return render_template('speech.html')


@main.route('/speech-analyse')
def speech_analyse():
    filename = url_for('static', filename=request.args.get('filename'))

    with io.open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    print(sys.getsizeof(audio_file))
    response = speech_client.recognize(speech_config, audio)

    transcript = ' '.join(result.alternatives[0].transcript for result in response.results)

    return transcript
