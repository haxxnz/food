import logging
import os

from flask import Flask, Blueprint, render_template
from flask_login import current_user, login_required, LoginManager

from data import db
from data.auth import User
from routes.auth import auth as auth_bp

_FLASK_CONFIG_TO_VARIABLE_MAPPING = [
    ("SQLALCHEMY_DATABASE_URI", "DATABASE_URL"),
    ("SECRET_KEY", "SECRET_KEY"),
]

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", name=current_user.display_name)


def init_app():
    app = Flask(__name__)

    for config, env_var_name in _FLASK_CONFIG_TO_VARIABLE_MAPPING:
        val = os.environ.get(env_var_name, None)
        if val is None:
            raise ValueError("Unable to start application, environment variable {} value missing".format(env_var_name))
        app.config[config] = val

    app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
    app.config["SESSION_COOKIE_SAMESITE"] = "strict"

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.filter_by(id=user_id).first()

    # register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app


if __name__ == "__main__":
    app = init_app()
    logging.basicConfig(level=logging.DEBUG)
    app.run(host="127.0.0.1", port=8080, debug=True)
