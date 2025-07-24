from middleman.jwt_helper import create_token, decode_token
from middleman.basic_auth import validate_basic_auth
from utils.validators import is_valid_email, is_valid_password
from model.user_model import insert_user, find_user_by_email, update_user, find_user_id_by_email
from utils.mail import send_email
from flask import request, jsonify
import bcrypt
import logging
from middleman.basic_auth import extract_and_validate_basic_auth
import random
import time


logger = logging.getLogger("controller_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("controller.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def signup(request):
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        logger.warning("User registration failed: Missing fields")
        return {"error": "All fields are required"}, 400
    
    if is_valid_email(email) == False:
        logger.warning(f"User registration failed: Invalid email format ({email})")
        return {"error": "Invalid email format"}, 400
    
    
    
    if not is_valid_password(password):
        logger.warning("User registration failed: Password does not meet complexity requirements")
        return {"error": "Password must be at least 8 characters long, contain uppercase, lowercase, digit, and special character"}, 400
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


    username_auth, password_auth, error_response, status_code = extract_and_validate_basic_auth()
    if error_response:
        logger.warning(f"User registration failed: {error_response['error']}")
        return error_response, status_code

    try:
        insert_user(username, email, hashed_password)
        logger.info(f"User registered successfully: {username} ({email})")
        send_email(email, "✅ User Registered", f"Your email {email} has been registered.")
        return {"message": "✅ user registered"}, 200

    except Exception as e:
        logger.error(f"User registration failed for {email}: {e}", exc_info=True)
        return {"error": f"User registration failed: {str(e)}"}, 401
    
def updateuser(request):
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    gender = data.get("gender")
    height = data.get("height")
    weight = data.get("weight")
    age = data.get("age")
    address = data.get("address")
    city = data.get("city")
    country = data.get("country")

    if not all([email]):
        logger.warning("User registration failed: Missing fields")
        return {"error": "All fields are required"}, 400
    
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"User sign-in failed: User not found ({email})")
        return {"error": "User not found"}, 404

    
    if gender != "male" and gender != "female":
        logger.warning(f"User registration failed: Invalid gender")
        return {"error": "Invalid Gender"}, 400
    
    if not is_valid_password(password):
        logger.warning("User registration failed: Password does not meet complexity requirements")
        return {"error": "Password must be at least 8 characters long, contain uppercase, lowercase, digit, and special character"}, 400
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    username_auth, password_auth, error_response, status_code = extract_and_validate_basic_auth()
    if error_response:
        logger.warning(f"User update failed: {error_response['error']}")
        return error_response, status_code
    
    try:

        fields = []
        values = []

        if username:
            fields.append("username = %s")
            values.append(username)
        if password:
            fields.append("password = %s")
            values.append(hashed_password)
        if gender:
            fields.append("gender = %s")
            values.append(gender)

        if height:
            fields.append("height = %s")
            values.append(height)

        if weight:
            fields.append("weight = %s")
            values.append(weight)

        if age:
            fields.append("age = %s")
            values.append(age)
        
        if address:
            fields.append("address = %s")
            values.append(address)

        if city:
            fields.append("city = %s")
            values.append(city)

        if country:
            fields.append("country = %s")
            values.append(country)

        if not fields:
            logger.warning("user update failed: No fields provided to update")
            return jsonify({"error": "No fields provided to update"}), 400

        success = update_user(email, fields, values)

        if success:
            logger.info(f"User details updated successfully for {email}")
            return jsonify({"message": "✅ user updated successfully"}), 200
        else:
            logger.error(f"user update failed for {email}")
            return jsonify({"error": "user update failed"}), 500

    except Exception as e:
        logger.error(f"user update failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Verification failed: {str(e)}"}), 401



# 5️⃣ Login
def signin(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = find_user_by_email(email)
    if not user:
        logger.warning(f"User sign-in failed: User not found ({email})")
        return {"error": "User not found"}, 404
    
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        logger.warning(f"User sign-in failed: Invalid credentials ({email})")
        return {"error": "Invalid credentials"}, 401
    
    username_auth, password_auth, error_response, status_code = extract_and_validate_basic_auth()
    if error_response:
        logger.warning(f"User registration failed: {error_response['error']}")
        return error_response, status_code

    try:
        x=find_user_id_by_email(email)
        token = create_token(x)
        logger.info(f"User signed in successfully: {email}")
        
        return {"✅ SIGN IN SUCCESS, token": token}, 200   

    except Exception as e:
        logger.error(f"User sign-in failed for {email}: {e}", exc_info=True)
        return {"error": f"Basic Auth Verification failed OR jwt FAILED: {str(e)}"}, 401
    
otp_store = {}
pending_users = {}
def sendotp(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = find_user_by_email(email)
    if not user:
        logger.warning(f"User sign-in failed: User not found ({email})")
        return {"error": "User not found"}, 404
    
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        logger.warning(f"User sign-in failed: Invalid credentials ({email})")
        return {"error": "Invalid credentials"}, 401
    
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "expires": time.time() + 300}
    pending_users[email] = {
        "username": email,
        "password": password
    }
    subject = "Your OTP Code"
    message = f"Hello {user['username']},\n\nYour OTP is: {otp}\n\nThanks!"
    send_email(email, subject, message)

    return {"message": "OTP sent to email"}, 200

def verify_otp(request):
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return {"error": "Email and OTP required"}, 400

    record = otp_store.get(email)
    if not record:
        return {"error": "No OTP found for this email"}, 404

    if time.time() > record["expires"]:
        del otp_store[email]
        return {"error": "OTP expired"}, 401

    if record["otp"] != otp:
        return {"error": "Incorrect OTP"}, 401

    user_data = pending_users.get(email)
    if not user_data:
        return {"error": "No pending user found"}, 404
    fields = ["verified = %s"]
    values = ['True']
    update_user(email, fields, values)
    del otp_store[email]
    del pending_users[email]

    return {"message": "✅ OTP verified, user registered"}, 200