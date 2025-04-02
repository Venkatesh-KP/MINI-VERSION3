import os
import time
import random
import bcrypt
import sqlite3
import csv
import PyPDF2
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import google.generativeai as palm

# Load environment variables
load_dotenv()

# Flask App Configuration
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"

# Database and File Paths
DB_PATH = "users.db"
CSV_FILE_PATH = "sample_data.csv"
PDF_PATH = "STUDENT_CODE_OF_CONDUCT.pdf"

# Securely Get Gemini API Key
gemini_api_key = "AIzaSyBWBxsPBykuJ6z_kMYlAq9k9u3YU2Uy8Oc"
if gemini_api_key:
    try:
        palm.configure(api_key=gemini_api_key)
        print("✅ Gemini API Connected!")
    except Exception as e:
        print(f"⚠️ Error configuring Gemini API: {e}")
else:
    print("⚠️ Warning: No Gemini API Key provided!")

# Initialize SQLite Database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                phone TEXT PRIMARY KEY,
                otp TEXT,
                otp_time INTEGER
            )
        """)
        conn.commit()

init_db()

# OTP Handling
def generate_otp():
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

def verify_hashed_otp(otp, hashed_otp):
    return bcrypt.checkpw(otp.encode(), hashed_otp.encode())

def send_otp(phone, otp):
    print(f"📩 FAKE OTP for {phone}: {otp}")  # Replace with actual SMS API

@app.route('/request-otp', methods=['POST'])
def request_otp():
    try:
        data = request.get_json()
        phone = data.get("phone")
        if not phone:
            return jsonify({"error": "Phone number is required"}), 400

        otp = generate_otp()
        hashed_otp = hash_otp(otp)
        otp_time = int(time.time())

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO users (phone, otp, otp_time) VALUES (?, ?, ?)", 
                           (phone, hashed_otp, otp_time))
            conn.commit()

        send_otp(phone, otp)
        return jsonify({"message": "OTP sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        phone = data.get("phone")
        otp = data.get("otp")

        if not phone or not otp:
            return jsonify({"error": "Phone and OTP required"}), 400

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT otp, otp_time FROM users WHERE phone = ?", (phone,))
            record = cursor.fetchone()

        if record:
            stored_hashed_otp, otp_time = record
            if verify_hashed_otp(otp, stored_hashed_otp) and int(time.time()) - otp_time <= 300:
                session["user"] = phone
                return jsonify({"message": "OTP verified successfully", "redirect": "/chatbot"}), 200
            else:
                return jsonify({"error": "Invalid or expired OTP"}), 400

        return jsonify({"error": "No OTP found for this number"}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/')
def index():
    return redirect(url_for("login")) if "user" not in session else redirect(url_for("chatbot"))

@app.route('/chatbot')
def chatbot():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chatbot.html")

# PDF Handling
def extract_pdf_text(pdf_path):
    text = ""
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"⚠️ Error extracting text from PDF: {e}")
    return text

pdf_text = extract_pdf_text(PDF_PATH)

def search_pdf_content(query):
    query_lower = query.lower()
    if query_lower in pdf_text.lower():
        start_idx = pdf_text.lower().find(query_lower)
        return pdf_text[max(0, start_idx - 100):start_idx + 300]
    return None

# AI Chat Integration
def generate_gemini_response(user_input):
    if not gemini_api_key:
        return "⚠️ Gemini API key not configured."
    try:
        response = palm.generate_text(
            model='models/text-bison-001',
            prompt=f"{pdf_text}\n\nUser: {user_input}\nBot:",
            temperature=0.7,
            max_output_tokens=256
        )
        return response.result if response else "⚠️ No response from Gemini."
    except Exception as e:
        return f"⚠️ Error using Gemini API: {str(e)}"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        if not user_input:
            return jsonify({"error": "No input provided."}), 400

        pdf_response = search_pdf_content(user_input)
        if pdf_response:
            return jsonify({"message": f"📄 Found in PDF: {pdf_response}"}), 200

        gemini_response = generate_gemini_response(user_input)
        return jsonify({"message": f"🤖 Gemini Response: {gemini_response}"}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
