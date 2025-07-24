from database.connection import get_connection
import logging

logger = logging.getLogger("model_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("model.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# 1️⃣ Insert a new user into the `project` table
def insert_user(username, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        logger.info(f"User created: {username} ({email})")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to insert user ({email}): {e}", exc_info=True)


def update_user(email, fields, values):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        set_clause = ", ".join(fields)
        sql = f"UPDATE users SET {set_clause} WHERE email = %s"
        values.append(email)
        cursor.execute(sql, values)
        conn.commit()
        logger.info(f"User updated: {email}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to update user ({email}): {e}", exc_info=True)
        return False
    
# 2️⃣ Find a user by email
def find_user_by_email(email):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
                logger.info(f"User found for email: {email}")
        else:
            logger.warning(f"No user found with email: {email}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user by email ({email}): {e}", exc_info=True)
        return None

def find_user_id_by_email(email):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            logger.info(f"User ID found for email: {email}")
            return result['id']
        else:
            logger.warning(f"No user ID found with email: {email}")
            return None
    except Exception as e:
        logger.error(f"Error fetching user ID by email ({email}): {e}", exc_info=True)
        return None
    
