from flask import Flask, request, session, render_template, redirect, url_for
from twilio.rest import Client
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for security

# Twilio Credentials (Replace with your actual details)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via Twilio SMS
def send_otp(phone_number, otp):
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid

# Route to render the login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to send OTP
@app.route('/send_otp', methods=['POST'])
def send_otp_to_user():
    phone_number = request.form.get('phone_number')
    
    if not phone_number:
        return "Please enter a valid phone number."

    session['phone_number'] = phone_number  # Store phone number in session
    otp = generate_otp()
    session['otp'] = otp  # Store OTP in session

    send_otp(phone_number, otp)
    return redirect(url_for('verify_page'))

# Route to render the OTP verification page
@app.route('/verify')
def verify_page():
    return render_template('verify.html')

# Route to verify OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form.get('otp')
    if user_otp == session.get('otp'):
        return "Login Successful!"
    else:
        return "Invalid OTP. Try again!"

if __name__ == '__main__':
    app.run(debug=True)
