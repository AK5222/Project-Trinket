import os
from supabase import create_client, Client
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import mimetypes
from werkzeug.utils import secure_filename
load_dotenv()


#set up supabase stuff - url and admin key should be in .env
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv('SUPABASE_ADMIN_KEY')
supabase: Client = create_client(url, key)

#reference file name
app = Flask(__name__)

#place where listing images will be stored before being uploaded to supabase
app.config['IMAGES'] = 'images'


#create index route - just shows main page
@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')


#page for creating new account
@app.route('/register')
def register():
    return render_template('register.html')


#page for seeing account details (current listings, etc)
@app.route('/account')
def account():
    return render_template('account.html')


#login page
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')   


#page for listing a new item to be put up for bidding
@app.route('/list', methods=['POST', 'GET'])
def list():
    #everything in the if statement is triggered once the "submit listing" button is pushed
    if request.method == 'POST':
        try:
            #make sure that name, bid, and condition are filled in - these are required
            name = request.form['name']
            bid = request.form['bid']
            condition = request.form['cond']
        #if one is missing throw exception - this should be changed later to let the
        #user know, and reprompt for input on the listing creation page
        except Exception as e:
            return jsonify({'error': f"Error getting form data: {e}"}), 400

        #second try catch block is to check for image stuff
        try:
            #ensure image was properly stored in request.files
            if 'image' not in request.files:
                return jsonify({'error': "No image part"}), 400
            image = request.files['image']
            #ensure image was uploaded in the first place
            if image.filename == '':
                return jsonify({'error': 'No selected image'}), 400

        #throw exception if something goes wrong with image upload
        except Exception as e:
            return jsonify({'error': f"Error handling image: {e}"}), 400

        # Sends us to a function that handles uploading the listing to supabase
        listingSuccess = createListing(name, bid, condition, request.form['desc'], image.filename)

        # Ensure the file has the correct MIME type (image/jpeg, image/png, etc.)
        if image.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']:
            return jsonify({'error': 'Invalid image format'}), 400

        #all of this is to store image in a local file that app.py can find
        #TODO: does not handle image files that have spaces in the name properly
        image_data = secure_filename(image.filename)
        basedir = os.path.abspath(os.path.dirname(__file__))
        image.save(os.path.join(basedir, app.config['IMAGES'], image_data))
        image_path='./images/'+image.filename

        #now that we have the image in a location we know, we can send the image to supabase
        with open(image_path, 'rb') as img:
            supabase.storage.from_('images').upload(file = image_path, path=image_path, file_options={'content-type':'image/jpeg','cache-control':'3600','upsert':'false'},)
        #send user to a page that informs them that the listing was created successfully
        return render_template('listingSuccess.html')
    
    #if something goes wrong and isnt caught by one of the excepts, send us back to list.html
    #TODO: This is bad, but temporary - issues with image/name etc should not jsonify, but should inform user with an error message within link.html
    return render_template('list.html')


#responsible for sending listings to supabase table
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