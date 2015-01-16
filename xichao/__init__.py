from flask import Flask
from database import db_session

app = Flask(__name__)
import views

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()