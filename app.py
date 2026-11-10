
import os

from flask import Flask, render_template

from config import Config
from extensions import db, login_manager, csrf

from models import User, Paper, Collection

from routes.auth import auth
from routes.dashboard import dashboard
from routes.research import research
from routes.lab import lab


def create_app():

    # Create Flask application
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Create upload directory
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."

    # Load logged-in users
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(research)
    app.register_blueprint(lab)

    # Homepage
    @app.route("/")
    def index():
        return render_template("index.html")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
