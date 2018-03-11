import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    TEXTS_PER_PAGE = int(os.environ.get('TEXTS_PER_PAGE'))

    # app.config['MODEL'] = 'data/lbg_culture_prop_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
    # app.config['MODEL_PHRASER'] = 'data/culture_prop_phraser_bigram-npmi'
    # app.config['MODEL_THEMES'] = 'data/LBG Culture - Sample Dictionary - Semantic v4.1.xlsx'

    MODEL = 'data/banking/banking_survey_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
    MODEL_PHRASER = 'data/banking/banking_survey_phraser_bigram-npmi'
    MODEL_THEMES = 'data/banking/Banking - Test Dictionary.xlsx'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}