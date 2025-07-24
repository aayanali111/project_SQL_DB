import jwt
import datetime
from flask import request, jsonify

SECRET_KEY = "myverysecretkey"

def create_token(x):
    return jwt.encode({
        "id": x,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def authorize_request():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, None, jsonify({"error": "Missing or invalid token"}), 401
    token = auth_header.split(" ")[1]
    try:
        decoded = decode_token(token)
        user_id = decoded.get("id")
        if user_id is None:
            return None, None, jsonify({"error": "User ID not found in token"}), 401
        return decoded, user_id, None, None
    except Exception as e:
        return None, None, jsonify({"error": f"Verification failed: {str(e)}"}), 401