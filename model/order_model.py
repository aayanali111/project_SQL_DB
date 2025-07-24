from database.connection import get_connection
import logging

logger = logging.getLogger("model_logger")
logger.setLevel(logging.INFO)
 
if not logger.handlers:
    file_handler = logging.FileHandler("model.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
 
def insert_order(user_id, product_id, address, city, country, zipcode, phone_number):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        print(user_id)
        result = cursor.fetchone()
        if not result:
            logger.warning(f"Insert failed: No user found with id {user_id}")
            cursor.close()
            conn.close()
            raise Exception("User not found")

        cursor.execute(
            "INSERT INTO orders (user_id, product_id, address, city, country, zipcode, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_id, product_id, address, city, country, zipcode, phone_number)
        )
        
        conn.commit()

        if cursor.rowcount == 0:
            logger.error(f"No rows inserted for user {user_id}")
            raise Exception("Insert failed")

        logger.info(f"✅ Order inserted for user {user_id}")
        cursor.close()
        conn.close()
        

    except Exception as e:
        logger.error(f"Error inserting order for {user_id}: {e}", exc_info=True)
        raise

def get_order_id(user_id, product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM orders WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result["id"]
        else:
            logger.warning(f"Order not found for user {user_id} and inventory {product_id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching order ID for user {user_id} and inventory {product_id}: {e}", exc_info=True)
        return None

def order_items(order_id, product_id, quantity, size, color, quality, product_price, product_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, product_size, product_color, product_quality, product_price, product_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (order_id, product_id, quantity, size, color, quality, product_price, product_name)
        )
        
        conn.commit()

        if cursor.rowcount == 0:
            logger.error(f"No rows inserted for order {order_id}")
            raise Exception("Insert failed")

        logger.info(f"✅ Order items inserted for order {order_id}")
        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error inserting order items for order {order_id}: {e}", exc_info=True)
        raise

def get_orders_by_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT o.id as cart_id, o.address, o.city, o.country, o.zipcode, o.phone_number, oi.product_id, oi.quantity, oi.product_size, oi.product_color, oi.product_quality, oi.product_price, oi.product_name FROM orders o JOIN order_items oi ON o.id = oi.order_id WHERE o.user_id = %s",
            (user_id,)
        )
        orders = cursor.fetchall()
        cursor.close()
        conn.close()

        if not orders:
            logger.warning(f"No orders found for user {user_id}")
            return None

        return orders
    except Exception as e:
        logger.error(f"Error fetching orders for user {user_id}: {e}", exc_info=True)
        return None
    

def update_order_item_model(order_id, product_id, quantity, size, color, quality):
    try:
        conn = get_connection()
        cursor = conn.cursor()

    
        cursor.execute(
            "UPDATE order_items SET quantity = %s, product_size = %s, product_color = %s, product_quality = %s WHERE order_id = %s AND product_id = %s",
            (quantity, size, color, quality, order_id, product_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            logger.error(f"No order_items updated for order {order_id} and inventory {product_id}")
            raise Exception("Update failed")
        logger.info(f"Order item updated for order {order_id} and inventory {product_id}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating order item for order {order_id}: {e}", exc_info=True)
        raise

def update_order_address_model(order_id, address, city, country, zipcode, phone_number):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            logger.warning(f"Order ID {order_id} not found in orders table")
            raise Exception("Order not found")

        cursor.execute(
            "UPDATE orders SET address = %s, city = %s, country = %s, zipcode = %s, phone_number = %s WHERE id = %s",
            (address, city, country, zipcode, phone_number, order_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            logger.error(f"No orders updated for order {order_id}")
            raise Exception("Update failed")
        logger.info(f"Order address updated for order {order_id}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating order address for order {order_id}: {e}", exc_info=True)
        raise


def delete_order(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))

        conn.commit()

        if cursor.rowcount == 0:
            logger.error(f"No rows deleted for order {order_id}")
            raise Exception("Delete failed")

        logger.info(f"✅ Order deleted with ID {order_id}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error deleting order with ID {order_id}: {e}", exc_info=True)
        raise Exception(f"Delete failed: {str(e)}")

def calculate_order_total(user_id):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(oi.product_price * oi.quantity)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = %s
    """, (user_id,))
    total = cursor.fetchone()[0]
    return round(total or 0, 2)

from model.inventory_model import get_inventory_item, update_inventory_quantity

def restore_inventory_for_order(order_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    order_items = cursor.fetchall()
    cursor.close()
    conn.close()
    for item in order_items:
        inventory = get_inventory_item(
            item["product_id"],
            item["product_size"],
            item["product_color"],
            item["product_quality"]
        )
        if inventory:
            restored_quantity = inventory["stock_quantity"] + item["quantity"]
            update_inventory_quantity(
                item["product_id"],
                item["product_size"],
                item["product_color"],
                item["product_quality"],
                restored_quantity
            )

def get_order_item(order_id, product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM order_items WHERE order_id = %s AND product_id = %s",
            (order_id, product_id)
        )
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        return item
    except Exception as e:
        logger.error(f"Error fetching order item for order {order_id} and product {product_id}: {e}", exc_info=True)
        return None