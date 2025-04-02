from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
import os
import time
import random
import bcrypt
import sqlite3

# Define Blueprint
auth_bp = Blueprint('auth', __name__)

# Database Path
DB_PATH = "users.db"

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

@auth_bp.route('/request-otp', methods=['POST'])
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

@auth_bp.route('/verify-otp', methods=['POST'])
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
            if int(time.time()) - otp_time > 300:
                return jsonify({"error": "OTP expired. Request a new one."}), 400

            if verify_hashed_otp(otp, stored_hashed_otp):
                session["user"] = phone
                return jsonify({"message": "OTP verified successfully", "redirect": url_for('index')}), 200
            else:
                return jsonify({"error": "Invalid OTP"}), 400

        return jsonify({"error": "No OTP found for this number"}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {e}"}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route('/login')
def login():
    return render_template("login.html")  # ✅ Now properly rendering the login page
