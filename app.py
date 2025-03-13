import os
import time
import listing
import supabase
import schedule
import threading
from supabase import create_client, Client
from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
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
CORS(app)


app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")  # Keep it secure
Session(app)

app.config['IMAGES'] = 'images'

@app.context_processor
def inject_user():
    return {"user_logged_in": 'user' in session}


#global dict for transferring listings from supabase to flask to the webpage
currListings={}


#create index route - just shows main page
@app.route('/', methods=['POST','GET'])
def index():
    global currListings

    #calculate time left to bid on current batch of sales, if any
    seconds_left = timeLeft()

    #render main page
    return render_template('index.html', currListings = currListings, seconds_left = seconds_left)




#page for seeing account details (current listings, etc) 
@app.route('/account')
def account():
    return render_template('account.html')




#page for creating new account
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        data = request.json
        email = data.get("email")
        password = data.get("password")

        try:
            user = supabase.auth.sign_up({"email": email, "password": password})
            return jsonify({"message": "User registered successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        return render_template('register.html')
      



#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        email = data.get("email")
        password = data.get("password")

        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if user:
                session['user'] = user.user.id  # Store user ID in session
                return jsonify({"message": "Login successful", "redirect": url_for('index')}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('index'))




@app.route('/list', methods=['POST', 'GET'])
def list():
    if request.method == 'POST':
        name = request.form['name']
        bid = request.form['bid']
        condition = request.form['cond']
        image = request.files.get('image')  # Use get to avoid KeyError if image is not provided

        if not image:
            return jsonify({'error': 'No image provided'}), 400  # Ensure the response is always JSON

        # Make sure image format is correct
        if image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            return jsonify({'error': 'Invalid image format'}), 400

        # Process image and listing (the rest of your code)
        response = createListing(name, bid, condition, request.form['desc'], image.filename)

        image_data = secure_filename(image.filename)
        image_filename = image.filename.replace(" ",'_')

        basedir = os.path.abspath(os.path.dirname(__file__))
        image.save(os.path.join(basedir, app.config['IMAGES'], image_data))

        image_name = str(response.data[0]['id'])
        image_path_raw = './images/' + image_filename
        image_path_new = './images/' + str(image_name)
        os.rename(image_path_raw, image_path_new)

        try:
            supabase.storage.from_('images').upload(file=image_path_new, path=image_name, file_options={'content-type': 'image/*', 'cache-control': '3600', 'upsert': 'false'})
        except Exception as e:
            print(f"Error occurred: {e}")
            supabase.table('Listings').select('image').lte('created_at', target_time.isoformat()).execute()
            supabase.delete().eq("id", image_name).execute()

        os.remove(image_path_new)

        return render_template('listingSuccess.html')
    
    return render_template('list.html')




#This page shows more information about a listing, and will give users the option to bid on them
@app.route('/listingPage/<int:listing_id>')
def listingPage(listing_id):
    global currListings

    #Make sure we're looking for a current listing. Might want to extend this later to allow users to see past bids but probably don't have time to implement this
    item = currListings.get(listing_id)
    if not item:
        return "Listing not found", 404
    
    #Serve listing page if listing is found
    return render_template("listingPage.html", listing=item)



#responsible for sending listings to supabase table
def createListing(name, bid, condition, description, image):
    try:
        #Send initial listing to supabase
        response = supabase.table('Listings').insert({'name': name, 'bid':bid, 'condition':condition,'description':description, 'image':image}).execute()

        #We want the image name to be the ID, which isn't generated until data is sent to supabase, so now we need to pull that and clean
        blah_int = response.data[0]['id']
        blah = str(blah_int)

        #update the listing in supabase to store the proper image name
        supabase.table('Listings').update({'image': blah}).eq('id', blah_int).execute()
        print('successfully added listing')
    except:
        print('listing fail :(')
        return None
    return response




#handles grabbing new listings for the current time window of sales
def fetchNewListings():
    #calculate the window of listings that should be grabbed - by default 30 minutes
    current_time = datetime.now(timezone.utc)
    delta = timedelta(minutes=30)
    listing_range = current_time - delta
    response = None
    try:
        #select all listings within the database that were submitted within the last 30 minutes
        response = supabase.table('Listings').select('*').gte('created_at', listing_range.isoformat()).execute()
    except Exception as e:
        print('something went wrong here:', e)

    return response




#cleans old listings from supabase and flask
def processListings():
    print('\n\nDeleting old listings...')

    #calculate timeframe of listings to delete - set to 31 minutes to make sure that processing time does not result in deleting listings that were made near a refresh. This may be bad/introduce bugs
    cur_time = datetime.now(timezone.utc)
    delta = timedelta(minutes=31)
    target_time = cur_time - delta
    try:
        #select all entries that were created 31+ minutes prior to call
        images_to_delete_raw = supabase.table('Listings').select('image').lte('created_at', target_time.isoformat()).execute()

        #iterate through each, and delete its associated image from the database
        for i in images_to_delete_raw.data:
            supabase.storage.from_("images").remove([i['image']])

        #once images are deleted, we can now safely remove all the old listings
        supabase.table('Listings').delete().lte('created_at', target_time.isoformat()).execute()
        print('Deletion of old listings successful.')

    except:
        print("failed to delete")


    #clear the global listing dict
    global currListings
    currListings.clear()

    #call updateListings
    updateListings()




#moves data from supabase into a dict so that flask can send it to the html page
def updateListings():
    print('\n\nAdding current listings to site...')
    global currListings

    #call fetchNewListings to give us all listings that should be displayed
    currListingsRaw = fetchNewListings()

    try:
        #iterate through dict of listings, and make each its own listing
        for i in currListingsRaw.data:
            print(type(i))
            print(i)
            try:
                temp = listing.Listing(i)
                listingName = temp.getId()
                 #store each listing as its id for a key within the currListings dict
                currListings[listingName] = temp
            except:
                print('Error adding this listing.')
                pass


            #temp.printInfo() #for debugging purposes
        #print(currListings) #for debugging purposes
    except Exception as e:
        print(f"Error while adding listings: {e}")
    
    print("Successfully added listings.")




#responsible for calculating the timer that gets displayed on the webpage
def timeLeft():
    cur_time = datetime.now(timezone.utc)

    #if minutes in current hour <30, calculate how long to get to x:30
    if cur_time.minute < 30:
        target_time = cur_time.replace(minute=30, second=0, microsecond=0)

    #if minutes in current hour 30+, calculate how long to get to x:00
    else:
        target_time = cur_time.replace(minute=0, hour=cur_time.hour + 1, second = 0, microsecond = 0)

    #calculate remaining time
    time_left = target_time - cur_time
    seconds_left = int(time_left.total_seconds())
    return seconds_left


#When debugging is set to true, the site will grab new listings every minute and will not remove old listings. When it is set to false,
#the site grabs new listings every 30 minutes and deletes all old listings within the Listings db.
debugging = True


#threading/scheduler required for scheduling tasks every half hour
def run_scheduler():
    global currListings
    if debugging:
        updateListings()
        schedule.every().minute.do(updateListings)

    else:
        schedule.every().hour.at(":00").do(processListings)
        schedule.every().hour.at(":30").do(processListings)
    
    while True:
        schedule.run_pending()
        time.sleep(1)


scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
if __name__ == "__main__":
    app.run(debug=debugging)