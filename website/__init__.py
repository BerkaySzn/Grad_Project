from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = "Grad_Project_DB"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key_here"

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mssql+pyodbc://@MELISA\\SQLSERVER/Grad_Project_DB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Bu import EN SONDA kalsın
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        with app.app_context():  # Context hatası engellenir
            return User.query.get(int(id))

    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    return app
