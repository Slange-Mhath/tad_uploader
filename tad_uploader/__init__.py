import os
from flask import Flask
from flask_dropzone import Dropzone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:////Users/sebastianlange/PycharmProjects/flaskProject/instance/tad_uploader.db'
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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import auth
    app.register_blueprint(auth.bp)
    from . import uploader
    app.register_blueprint(uploader.bp)
    app.add_url_rule('/', endpoint='index')
    dropzone = Dropzone()
    dropzone.init_app(app)
    db.init_app(app)

    return app
