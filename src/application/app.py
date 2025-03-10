# GET REQ: curl http://127.0.0.1:5555/second_endpoint
# POST REQ: Invoke-WebRequest -Uri "http://127.0.0.1:5555/second_endpoint" -Method Post

#


from flask import Flask
from routes import app_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')

    app.config['DATABASE_URI'] = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-OPP7BQ4\\MSSQLSERVER01;DATABASE=Grad_Project_DB;'
        'TrustServerCertificate=yes;Trusted_Connection=yes;'
    )

    app.register_blueprint(app_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

