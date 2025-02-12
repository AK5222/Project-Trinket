import os
from supabase import create_client, Client
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import mimetypes
from werkzeug.utils import secure_filename
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv('SUPABASE_ADMIN_KEY')
supabase: Client = create_client(url, key)

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

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')   

@app.route('/list', methods=['POST','GET'])
def list():
    if request.method == 'POST':
        try:
            name = request.form['name']
            bid = request.form['bid']
            condition = request.form['cond']
        except:
            return render_template('list.html')
        try:
            print('1')
            if 'image' not in request.files:
                return jsonify({'error': "No image part"}), 400
            print('2')
            image = request.files['image']
            print('3')
            print(os.path.abspath(image))
            print('\n\n\n\n\n\n\n\n\n\n\n')

            if image.filename == '':
                return jsonify({'error': 'No selected image'}), 400
            
        except:
            print('failure! embarassing!!!')
            return render_template('list.html')
        
        listingSuccess = createListing(name, bid, condition, request.form['desc'], image.filename)


        with open(image, 'rb') as img:
            imageSuccess = supabase.storage.from_('listingImages').upload(image.filename, img)

        print('blebleble')
        if not imageSuccess:
            #needs to return no image error
            return jsonify({'error': "Image upload failed"}), 400
        
        return render_template('listingSuccess.html')
    #needs to return an error and tell user what input they're missing
    return render_template('list.html')


@app.route('/listingSuccess/<int:id>')
def createListing(id):

    return 0
    
def createListing(name, bid, condition, description, image):
    success = True
    try:
        supabase.table('Listings').insert({'name': name, 'bid':bid, 'condition':condition,'description':description, 'image':image}).execute()
        print('successfully added listing')
    except:
        success = False
        print('listing fail :(')
    return success

if __name__ == "__main__":
    app.run(debug=True)