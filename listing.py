import os
import supabase
from supabase import create_client, Client
from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import mimetypes
from werkzeug.utils import secure_filename
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv('SUPABASE_ADMIN_KEY')
supabase: Client = create_client(url, key)


#store listing. Takes item from currListings dict from app.py as input
class Listing():
    def __init__(self, listingInfo):
        self.id = listingInfo['id']
        self.name = listingInfo['name']
        self.bid = listingInfo['bid']
        self.condition = listingInfo['condition']
        self.description = listingInfo['description']

        #stores signed url of image rather than image itself so we don't have to redownload the image
        self.imageURL = supabase.storage.from_('images').create_signed_url(listingInfo['image'], 100000)['signedURL']

    def getId(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getBid(self):
        return self.bid
    
    def getCondition(self):
        return self.condition
    
    def getURL(self):
       return self.imageURL

    #checks if user's bid beats current bid, updates highest bid on listing if true
    def updateBid(self, newBid):
        if newBid > self.bid:
            self.bid = newBid
            return supabase.table('Listings').update({'bid': newBid}).eq('id', self.id).execute()
        

    #for debugging purposes - print listing info to terminal
    def printInfo(self):
        print(f"-----------Listing ID {self.id}-----------")
        print(f'Name: {self.name}')
        print(f'Current Bid: {self.bid}')
        print(f'Description: {self.description}')
        print(f'Condition: {self.condition}\n\n\n')
