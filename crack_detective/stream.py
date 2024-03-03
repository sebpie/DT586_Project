from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from crack_detective.auth import login_required
from crack_detective.db import get_db

bp = Blueprint('stream', __name__)

#API endpoint for streaming webcam feed
@bp.route('/')
@login_required
def index():
    return render_template('stream/index.html')
