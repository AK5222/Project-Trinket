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

class Listing():
    def __init__(self, listingInfo):
        self.id = listingInfo['id']
        self.name = listingInfo['name']
        self.bid = listingInfo['bid']
        self.condition = listingInfo['condition']
        self.description = listingInfo['description']
        self.imageURL = supabase.storage.from_('images').create_signed_url(listingInfo['image'], 3600)['signedUrl']

    def getName(self):
        return self.name
    
    def getBid(self):
        return self.bid
    
    def getCondition(self):
        return self.condition
    
    def getURL(self):
        print(self.imageURL)
        return self.imageURL

    def updateBid(self, newBid):
        if newBid > self.bid:
            self.bid = newBid
            return supabase.table('Listings').update({'bid': newBid}).eq('id', self.id).execute()