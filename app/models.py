import os, io
from datetime import datetime
from flask import current_app
from app import db, classifier, sentiment, speech_client, speech_config, types
from threading import Thread


class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    sentences = db.relationship('Sentence', backref='text')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def classify_themes(self, split_sentences=True):
        predictions = classifier.predict(self.text, split_sentences)
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
    filename = db.Column(db.String, default=None, nullable=True)
    filepath = db.Column(db.String)
    url = db.Column(db.String, default=None, nullable=True)
    status = db.Column(db.String)
    transcript = db.Column(db.Text)
    text_id = db.Column(db.Integer, db.ForeignKey('texts.id'))
    text = db.relationship("Text", uselist=False)

    def delete(self):
        # os.remove(audios.path(self.filename))
        os.remove(self.filepath)
        db.session.delete(self)

    def transcribe(self):
        app = current_app._get_current_object()
        thr = Thread(target=self.transcribe_async, args=[self.id, app])
        thr.start()
        return thr

    @staticmethod
    def transcribe_async(audio_id, app):
        with app.app_context():
            audio = Audio.query.filter_by(id=audio_id).first()

            try:
                audio.status = 'Processing'
                audio.transcript = 'Audio file is currently being processed. Please refresh page or come back later.'
                db.session.add(audio)
                db.session.commit()

                with io.open(audio.filepath, 'rb') as audio_file:
                    content = audio_file.read()
                    data = types.RecognitionAudio(content=content)

                response = speech_client.recognize(speech_config, data)

                transcript = ' '.join(result.alternatives[0].transcript for result in response.results)

                audio.status = 'Completed'
                audio.transcript = transcript
                audio.text = Text(text=transcript)
                audio.text.classify_themes(split_sentences=False)

            except Exception as err:
                audio.status = 'Error'
                audio.transcript = str(err)
            db.session.add(audio)
            db.session.commit()


    def __repr__(self):
        return '<Audio: {} Timestamp: {}>'.format(self.title, self.timestamp)