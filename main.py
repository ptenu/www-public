from werkzeug.exceptions import HTTPException

from flask import render_template, Response

from app import app
from routes import *


@app.errorhandler(HTTPException)
def handle_errors(e):
    return Response(render_template("http_error.html", error=e), e.code)
