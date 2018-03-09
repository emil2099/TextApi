import os
from flask import Flask, render_template, session, redirect, url_for

from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand


from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from classifier.theme_classification import ThemeClassifier

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'word2vec!dem0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MODEL'] = 'data/lbg_culture_prop_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
app.config['MODEL_PHRASER'] = 'data/culture_prop_phraser_bigram-npmi'
app.config['MODEL_THEMES'] = 'data/LBG Culture - Sample Dictionary - Semantic v4.1.xlsx'
classifier = ThemeClassifier(app.config['MODEL'], app.config['MODEL_PHRASER'], app.config['MODEL_THEMES'])


def make_shell_context():
    return dict(app=app, db=db, Text=Text, Sentence=Sentence, Theme=Theme)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sentences = db.relationship('Sentence', backref='text')

    def classify_themes(self):
        predictions = classifier.predict(self.text)
        for prediction in predictions:
            sentence = Sentence(sentence=prediction['sentence'])
            self.sentences.append(sentence)
            themes = [Theme(theme=theme, score=score) for theme, score in prediction['themes']]
            sentence.themes.append(themes)

    def __repr__(self):
        return '<Text: {}>'.format(self.text)


class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text)
    text_id = db.Column(db.Integer, db.ForeignKey('texts.id'))
    themes = db.relationship('Theme', backref='sentence')

    def __repr__(self):
        return '<Sentence: {}>'.format(self.sentence)


class Theme(db.Model):
    __tablename__ = 'themes'
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.Text)
    score = db.Column(db.Float)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))

    def __repr__(self):
        return '<Theme: {}>'.format(self.theme)


class TextInput(FlaskForm):
    text = StringField('Enter text to classify', validators=[DataRequired()])
    submit = SubmitField('Find themes')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/classify', methods=['GET', 'POST'])
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
        return redirect(url_for('classify_text'))
    text = Text.query.filter_by(id=session.pop('text_id', None)).first()
    # text = session.pop('text', None)
    # sentences = session.pop('sentences', [])
    return render_template('classify.html', form=form, text=text)


# TODO Develop into returning all previous results
@app.route('/history', methods=['GET', 'POST'])
def classify_text():

    return render_template('classify.html', form=form, text=text)


if __name__ == '__main__':
    manager.run()