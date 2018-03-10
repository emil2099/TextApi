from flask import render_template, redirect, url_for, request, current_app, session

from app import db
from app.main import main
from app.main.forms import TextInput
from app.models import Text


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
