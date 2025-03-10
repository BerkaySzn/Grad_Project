#

from flask import Blueprint, render_template

app_bp = Blueprint('main', __name__, template_folder="templates")

@app_bp.route('/')
def index():
  return render_template('home_page.html')