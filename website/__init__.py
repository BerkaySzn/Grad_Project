from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize SQLAlchemy
db = SQLAlchemy()
DB_NAME = "Grad_Project_DB"  # User's database name

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this in production
    
    # MSSQL connection string with Windows Authentication
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://DESKTOP-OPP7BQ4\\MSSQLSERVER01/Grad_Project_DB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Import and register blueprints
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Import models
    from .models import User
    
    # Create database tables if they don't exist
    # Note: For a pre-existing database, you might not need this
    # with app.app_context():
    #     db.create_all()
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app
