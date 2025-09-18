import os

from flask import Flask, redirect, url_for, session,g
from .dashboardbp import dashboardbp
from .endpoints import chart_bp
from .auth import authbp
from .database import init_db


def create_app(test_config=None):
    # create and configure the appcle
    DB = os.getenv("DATABASE_NAME")
    USER = os.getenv("USER_NAME")
    HOST = os.getenv("HOST")
    PASSWORD = os.getenv("PASSWORD")
    app = Flask(__name__, instance_relative_config=True)
    connection_string = f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}:3306/{DB}"
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = connection_string
    )
    @app.before_request
    def load_user():
        g.user_id = session.get('user_id')
        g.username = session.get('username')

    init_db()
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    app.register_blueprint(authbp)
    app.register_blueprint(dashboardbp)
    app.register_blueprint(chart_bp)
    

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

    return app