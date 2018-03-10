from flask_migrate import Migrate

from app import create_app, db
from app.models import Text, Sentence, Theme

app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Text=Text, Sentence=Sentence, Theme=Theme)
