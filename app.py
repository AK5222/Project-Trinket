# Main Flask backend file
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import supabase
import config

app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

# Connect to Supabase
supabase_client = supabase.create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

@app.route("/")
def home():
    return render_template("login.html")  # Serve the login page

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user = supabase_client.auth.sign_up({"email": email, "password": password})
        return jsonify({"message": "User registered successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        user = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({"message": "Login successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)