# GET REQ: curl http://127.0.0.1:5555/second_endpoint
# POST REQ: Invoke-WebRequest -Uri "http://127.0.0.1:5555/second_endpoint" -Method Post

# v

#I installed chocolatey and CURL,

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')

    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@DESKTOP-OPP7BQ4\\MSSQLSERVER01/Grad_Project_DB?driver=ODBC+Driver+17+for+SQL+Server;TrustServerCertificate=yes;trusted_connection=yes'


    app.config['SQLALCHMEY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    migrate = Migrate(app, db)

    return app

import pyodbc
print(pyodbc.drivers())
