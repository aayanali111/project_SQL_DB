from flask import request

def validate_basic_auth(username, password):
    valid_username = "admin"
    valid_password = "admin@123"
    return username == valid_username and password == valid_password


def extract_and_validate_basic_auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Basic "):
        return None, None, {"error": "Missing or invalid token"}, 401
    try:
        import base64
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        if not validate_basic_auth(username, password):
            return None, None, {"error": "Invalid Basic Auth credentials"}, 403
        return username, password, None, None
    except Exception as e:
        return None, None, {"error": f"Basic Auth Verification failed: {str(e)}"}, 401