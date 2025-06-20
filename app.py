from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
from cryptography.fernet import Fernet
import os
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")  # Secure key storage

# -------------------- Database Configuration -------------------- #
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------- User Model -------------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# -------------------- Database Initialization -------------------- #
with app.app_context():
    db.create_all()

# -------------------- Encryption Functions -------------------- #
KEY_FILE = "secret.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Encryption key not found!")
    return open(KEY_FILE, "rb").read()

def encrypt_message(message):
    f = Fernet(load_key())
    return f.encrypt(message.encode())

def decrypt_message(encrypted_message):
    f = Fernet(load_key())
    return f.decrypt(encrypted_message).decode()

# -------------------- Authentication Routes -------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id  # Store user ID instead of username
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials! Try again.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# -------------------- Main Application Routes -------------------- #
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    try:
        result = subprocess.run(
            ["python", "face_authentication.py"], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
        )
        return jsonify({"success": "Access Granted" in result.stdout})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized! Please log in."})
    try:
        data = request.json
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"success": False, "error": "No message provided!"})
        encrypted_message = encrypt_message(message)
        return jsonify({"success": True, "encrypted_message": encrypted_message.decode()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized! Please log in."})
    try:
        result = subprocess.run(
            ["python", "face_authentication.py"], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
        )
        if "Access Granted" not in result.stdout:
            return jsonify({"success": False, "error": "Face authentication failed. Access Denied!"})

        data = request.json
        encrypted_message = data.get("encrypted_message", "").strip()
        if not encrypted_message:
            return jsonify({"success": False, "error": "No encrypted message provided!"})
        decrypted_message = decrypt_message(encrypted_message.encode())
        return jsonify({"success": True, "decrypted_message": decrypted_message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    import os
    generate_key()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

