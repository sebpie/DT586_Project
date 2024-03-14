import os
from dotenv import load_dotenv
from flask import Flask

from . import video
from . import home

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'crack_detective.sqlite'),
        MODEL= os.environ.get("MODEL", "VGG16"),
        MODEL_FILE = os.environ.get("MODEL_FILE", "test101.keras"),
        MODEL_SIZE_X = int(os.environ.get("MODEL_SIZE_X", 224)),
        MODEL_SIZE_Y = int(os.environ.get("MODEL_SIZE_Y", 224)),
        MODEL_SIZE_C= int(os.environ.get("MODEL_SIZE_C", 3)),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db
    db.init_app(app)

    video.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    home.init_home(app)
    app.register_blueprint(home.bp)

    app.add_url_rule('/', endpoint='home')

    return app