from database.connection import get_connection
import logging

logger = logging.getLogger("model_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("model.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def add_to_cart(user_id, product_id, quantity, size, color, quality, stock_quantity, product_price):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO cart_items 
            (user_id, product_id, quantity, product_size, product_color, product_quality, stock_quantity, product_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (user_id, product_id, quantity, size, color, quality, stock_quantity, product_price)

        cursor.execute(sql, values)
        conn.commit()

    except Exception as e:
        logger.error(f"Error adding item to cart: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def get_cart_items():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT 
                i.product_name, 
                ci.id as cart_id,
                ci.product_id,
                ci.product_price,
                ci.product_color, 
                ci.product_size, 
                ci.product_quality, 
                ci.quantity
            FROM cart_items ci
            JOIN inventory i ON ci.product_id = i.product_id
        ''')

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    except Exception as e:
        logger.error(f"Error fetching cart items: {e}", exc_info=True)
        return []

def update_to_cart(product_id, quantity, size, color, quality, cart_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE cart_items
            SET quantity = %s,
                product_size = %s,
                product_color = %s,
                product_quality = %s,
                product_id = %s
            WHERE id = %s
        """, (quantity, size, color, quality, product_id, cart_id))

        conn.commit()

    except Exception as e:
        logger.error(f"Error updating cart item: {e}", exc_info=True)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def delete_from_cart( cart_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM cart_items WHERE id = %s",
        (cart_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def check_cart_item(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cart_items WHERE product_id = %s", (product_id,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        if item:
            return item
        else:
            logger.warning(f"Cart item not found for product_id: {product_id}")
            return None
    except Exception as e:
        logger.error(f"Error checking user ID ({product_id}): {e}", exc_info=True)
        return None
    


def is_valid_cart_id(cart_id):

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cart_items WHERE id = %s", (cart_id,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        if item:
            return True
        else:
            logger.warning(f"Invalid cart ID: {cart_id}")
            return False
    except Exception as e:
        logger.error(f"Error checking cart ID ({cart_id}): {e}", exc_info=True)
        return False


def get_cart_items_by_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT *, id as cart_id FROM cart_items WHERE user_id = %s", (user_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error fetching cart items for user ID ({user_id}): {e}", exc_info=True)
        return []
    