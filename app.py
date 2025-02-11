from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#reference file name
app = Flask(__name__)


#create index route
@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/login')
def login():
    return render_template('login.html')   

@app.route('/list')
def list():
    return render_template('list.html')


if __name__ == "__main__":
    app.run(debug=True)