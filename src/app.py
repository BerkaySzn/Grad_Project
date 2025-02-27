# GET REQ: curl http://127.0.0.1:5555/second_endpoint
# POST REQ: Invoke-WebRequest -Uri "http://127.0.0.1:5555/second_endpoint" -Method Post

# .venv\Scripts\Activate 

#I installed chocolatey and CURL

from flask import Flask, request, make_response, render_template 
 
app = Flask(__name__, template_folder='templates')



@app.route('/')
def index():
  response = make_response('This iss the main page\n  ')
  response.status_code = 202
  response.headers['content-type'] = 'text/plain',
  return response  


@app.route('/recipes')
def recipes():
  myvalue = 'myvalue'
  myresult = 2 + 2
  return render_template('index.html', myvalue=myvalue, myresult=myresult)

@app.route('/second_endpoint', methods = ['GET', 'POST'])
def hello(): 
  if request.method == 'GET':
    return "You made a GET request"
  elif request.method == 'POST':
    return "You made a POST request"
  else:
    return "You hacked the system"



@app.route('/greet/<name>')
def greet(name):
  if 'greeting' in request.args.keys() and 'name' in request.args.keys():
    greeting = request.args.get('greetings')
    name = request.args.get('name')
    return f'{greeting}, {name}'
  else:
    return 'Some parameters are missing'

@app.route('/handşe_url_params')
def handle_params():
  return str(request.args)


 
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5555, debug = True)


  