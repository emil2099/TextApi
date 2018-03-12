import os
from flask_migrate import Migrate, upgrade

from app import create_app, db
from app.models import Text, Sentence, Theme

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(application, db)


@application.shell_context_processor
def make_shell_context():
    return dict(app=application, db=db, Text=Text, Sentence=Sentence, Theme=Theme)


@application.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@application.cli.command()
def deploy():
    """Run deployment tasks."""
    # Migrate database to latest revision
    upgrade()
    print('Deploy')