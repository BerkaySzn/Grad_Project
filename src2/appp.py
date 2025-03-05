# GET REQ: curl http://127.0.0.1:5555/second_endpoint
# POST REQ: Invoke-WebRequest -Uri "http://127.0.0.1:5555/second_endpoint" -Method Post

# .venv\Scripts\Activate 

#I installed chocolatey and CURL

import pandas as pd
from flask import Flask, request, make_response, render_template 
 
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')



@app.route('/')
def index():
    return render_template('home_page.html')

  

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('loginn.html')
  elif request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'abc' and password == '123':
      return render_template('photo_upload.html')
    else:
      return "Failure"


@app.route('/photo_upload', methods = ['GET', 'POST'])
def photo_upload(): 
  if request.method == 'GET':
    return render_template('photo_upload.html')
  elif request.method == 'POST':
    return "Photo uploaded"

 

@app.route('/recipes')
def recipes():
  return render_template('recipess.html')


 
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5555, debug = True)


  