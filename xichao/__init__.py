from flask import Flask
from database import db_session

app = Flask(__name__)
import views

app.secret_key = '\x18\xd1\x81cU\xb9j%\xb9\x00\xf5\xf3\xe9r\xcb\x82lq\x9e\xa8\xe3\x14@\x96'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()