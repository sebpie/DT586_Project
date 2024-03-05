import os

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
    image_names = os.listdir('crack_detective/static/images')
    return render_template('stream/index.html', image_names=image_names)


#API to fetch pictures from current directory and display them
