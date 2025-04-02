import random
from twilio.rest import Client

# Twilio credentials (replace with your own)
ACCOUNT_SID = "your_twilio_account_sid"
AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"  # Your Twilio phone number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_otp(phone_number):
    """Generates and sends an OTP to the given phone number."""
    otp = random.randint(100000, 999999)
    
    message_body = f"Dear user,\n\nYour OTP is {otp}."
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    print(f"OTP has been sent to {phone_number}")
    return otp

def verify_phone_number(phone_number):
    """Checks if the phone number is valid (basic check for length and digits)."""
    if phone_number.startswith("+") and phone_number[1:].isdigit() and 10 <= len(phone_number[1:]) <= 15:
        return phone_number
    else:
        print("Invalid phone number format. Please enter in international format (e.g., +1234567890).")
        return verify_phone_number(input("Enter a valid phone number: "))

# Get user details
name = input("Enter your name: ")
phone_number = input("Enter your phone number (with country code): ")
valid_phone_number = verify_phone_number(phone_number)

# Send OTP
OTP = send_otp(valid_phone_number)

# OTP Verification
received_OTP = int(input("Enter OTP: "))

if received_OTP == OTP:
    print("OTP verified successfully!")
else:
    print("Invalid OTP!")
    answer = input("Enter 'yes' to resend OTP to the same number or 'no' to enter a new phone number: ").strip().lower()
    
    if answer == "yes":
        OTP = send_otp(valid_phone_number)
    elif answer == "no":
        new_phone_number = input("Enter new phone number: ")
        valid_phone_number = verify_phone_number(new_phone_number)
        OTP = send_otp(valid_phone_number)
    else:
        print("Invalid input.")
