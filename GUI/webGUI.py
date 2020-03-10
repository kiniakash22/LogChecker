from flask import Flask, session, request, redirect, url_for, render_template
import xml.dom.minidom
import ssh_login
from datetime import timedelta

timeout = 250

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(seconds=timeout)
app.secret_key = "###secretkey###"

doc = ""
@app.before_first_request
def init():
    global doc
    doc = xml.dom.minidom.parse("./configuration.xml") 
    
@app.route('/', methods=['GET'])
def login():
    if "username" in session:
        return redirect(url_for("home",name=session["username"]))
    return render_template("login.html")

 
@app.route('/authenticator', methods=['POST'])
def authenticator():
    username = request.form.get('name')
    password = request.form.get('pass')
    if ssh_login.login(username, password):
        session["username"] = username
        return redirect(url_for("home",name=username))
    return redirect(url_for("login"))
 
@app.route('/home/<name>')
def home(name):
   return render_template("success.html", name=name)

@app.route('/logout')
def logout():
   if "username" in session:
       session.pop("username")
   return redirect(url_for("login"))
app.run(debug=True)