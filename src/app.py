# GET REQ: curl http://127.0.0.1:5555/second_endpoint
# POST REQ: Invoke-WebRequest -Uri "http://127.0.0.1:5555/second_endpoint" -Method Post

# .venv\Scripts\Activate 

#I installed chocolatey and CURL

import pandas as pd
from flask import Flask, request, make_response, render_template 
 
app = Flask(__name__, template_folder='templates')



@app.route('/')
def index():
  response = make_response('This iss the main page\n  ')
  response.status_code = 202
  response.headers['content-type'] = 'text/plain',
  return response  


@app.route('/login_page', methods = ['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('index.html')
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



@app.route('/greet/<name>')
def greet(name):
  if 'greeting' in request.args.keys() and 'name' in request.args.keys():
    greeting = request.args.get('greetings')
    name = request.args.get('name')
    return f'{greeting}, {name}'
  else:
    return 'Some parameters are missing'

@app.route('/handle_url_params')
def handle_params():
  return str(request.args)


 
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5555, debug = True)


  