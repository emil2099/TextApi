from datetime import datetime
from app import db, classifier, sentiment


class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sentences = db.relationship('Sentence', backref='text')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def classify_themes(self):
        predictions = classifier.predict(self.text)
        for prediction in predictions:
            sentence = Sentence(sentence=prediction['sentence'],
                                sentiment=sentiment.polarity_scores(prediction['sentence'])['compound'])
            self.sentences.append(sentence)
            themes = [Theme(theme=theme, score=score) for theme, score in prediction['themes']]
            sentence.themes.extend(themes)

    def __repr__(self):
        return '<Text: {}>'.format(self.text)


class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text)
    sentiment = db.Column(db.Float)
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


class Audio(db.Model):
    __tablename__ = 'audio'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    audio_filename = db.Column(db.String, default=None, nullable=True)
    audio_url = db.Column(db.String, default=None, nullable=True)

    def __repr__(self):
        return '<Audio: {} Timestamp: {}>'.format(self.title, self.timestamp)