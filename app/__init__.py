import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_uploads import UploadSet, configure_uploads, patch_request_class

from app.classifier.theme_classification import ThemeClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from config import config


from flask_script import Manager
manager = Manager()  # TODO is this needed

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
audios = UploadSet(name='audios', extensions='wav')

MODEL = 'app/data/banking/banking_survey_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
MODEL_PHRASER = 'app/data/banking/banking_survey_phraser_bigram-npmi'
MODEL_THEMES = 'app/data/banking/Banking - Test Dictionary.xlsx'
classifier = ThemeClassifier(MODEL, MODEL_PHRASER, MODEL_THEMES)
sentiment = SentimentIntensityAnalyzer()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    configure_uploads(app, audios)
    patch_request_class(app)

    from app.main import main
    app.register_blueprint(main)

    if config_name == 'beanstalk':
        file_handler=RotatingFileHandler('/opt/python/log/my.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('TextApi startup')

    return app
