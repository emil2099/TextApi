from flask import render_template, redirect, url_for, request, current_app, session, flash, abort

from app import db, audios
from app.main import main
from app.main.forms import TextInput, AudioUpload, flash_errors
from app.models import Text, Audio


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


@main.route('/audio')
def audio_list():
    page = request.args.get('page', type=int)
    pagination = Audio.query.order_by(Audio.timestamp.desc()).paginate(
        page, per_page=current_app.config['TEXTS_PER_PAGE'], error_out=False)
    audios = pagination.items
    return render_template('audio.html', audios=audios, pagination=pagination)


@main.route('/audio-upload', methods=['GET', 'POST'])
def upload_audio():
    form = AudioUpload()
    if request.method == 'POST':
        if form.validate_on_submit():
            filename = audios.save(request.files['audio_file'])
            audio = Audio(title=form.title.data, description=form.description.data, filename=filename,
                          filepath=audios.path(filename), url=audios.url(filename))
            db.session.add(audio)
            db.session.commit()
            audio.transcribe()
            flash('New audio file, {}, added'.format(audio.title), 'success')
            session['audio_id'] = audio.id
            return redirect(url_for('main.audio_list'))
        else:
            flash_errors(form)
            flash('ERROR! Audio was not added.', 'error')
    return render_template('upload-audio.html', form=form)


@main.route('/audio/<id>')
def audio_detail(id):
    audio = Audio.query.filter_by(id=id).first()
    if audio is None:
        abort(404)
    return render_template('audio_detail.html', audio=audio)


@main.route('/audio/delete/<id>', methods=['POST'])
def delete_audio(id):
    audio = Audio.query.filter_by(id=id).first()
    if audio is None:
        abort(401)
    audio.delete()
    flash('Audio deleted')
    return redirect(url_for('main.audio_list'))

