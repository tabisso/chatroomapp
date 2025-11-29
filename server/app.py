#Server app for the project 
from flask import Flask , request, jsonify
from werkzeug.exceptions import HTTPException

from db import init_db, create_user, verify_user, add_message, get_messages_after   

app = Flask(__name__)


# ---------- Error handling ----------


@app.errorhandler(Exception)
def handle_errors(error):
    """
    Return nice JSON errors instead of HTML.
    """
    