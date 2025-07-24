from database.connection import get_connection
import logging

logger = logging.getLogger("model_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("model.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def fetch_all_inventory():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                product_name, 
                description, 
                product_id
            FROM inventory;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error fetching product list: {e}", exc_info=True)
        return []

    
def check_id(product_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id FROM inventory WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result.get("product_id"):
            logger.info(f"Product ID exists: {product_id}")
            return result["product_id"]
        else:
            logger.warning(f"Product ID not found: {product_id}")
            return None
    except Exception as e:
        logger.error(f"Error checking Product ID ({product_id}): {e}", exc_info=True)
        return None

def get_product_name(product_id, size, color, quality):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT v.*, i.product_name 
        FROM variants v
        JOIN inventory i ON v.product_id = i.product_id
        WHERE v.product_id = %s 
        AND v.product_size = %s 
        AND v.product_color = %s 
        AND v.product_quality = %s
    ''', (product_id, size, color, quality))

    item = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return item['product_name'] if item else None



def get_inventory_item(product_id, size, color, quality):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT 
            inv.id AS inventory_id,
            inv.category_id,
            inv.product_name,
            inv.product_image,
            inv.description,
            inv.created_at,
            inv.updated_at,
            v.id AS variant_id,
            v.product_size,
            v.product_color,
            v.product_price,
            v.product_quality,
            v.stock_quantity,
            v.product_discount
        FROM inventory AS inv
        JOIN variants AS v ON inv.product_id = v.product_id
        WHERE v.product_id = %s 
          AND v.product_size = %s 
          AND v.product_color = %s 
          AND v.product_quality = %s
        ''',
        (product_id, size, color, quality)
    )

    item = cursor.fetchone()
    cursor.close()
    conn.close()
    return item


def update_inventory_quantity(product_id, size, color, quality, new_quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE variants 
        SET stock_quantity = %s 
        WHERE product_id = %s 
          AND product_size = %s 
          AND product_color = %s 
          AND product_quality = %s
        """,
        (new_quantity, product_id, size, color, quality)
    )
    conn.commit()
    cursor.close()
    conn.close()


