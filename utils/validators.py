from email_validator import validate_email, EmailNotValidError

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

import re

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Uppercase
        return False
    if not re.search(r'[a-z]', password):  # Lowercase
        return False
    if not re.search(r'\d', password):     # Digit
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Special character
        return False
    return True

def is_valid_quantity(quantity):
    return isinstance(quantity, int) and quantity > 0



