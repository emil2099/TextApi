import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

from app.classifier.theme_classification import ThemeClassifier
from config import Config


from flask_script import Shell
from flask_script import Manager
manager = Manager()  # TODO is this needed

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

MODEL = 'app/data/banking/banking_survey_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
MODEL_PHRASER = 'app/data/banking/banking_survey_phraser_bigram-npmi'
MODEL_THEMES = 'app/data/banking/Banking - Test Dictionary.xlsx'
classifier = ThemeClassifier(MODEL, MODEL_PHRASER, MODEL_THEMES)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler=RotatingFileHandler('logs/textapi.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('TextApi startup')

    return app
