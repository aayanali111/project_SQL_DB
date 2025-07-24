from model.order_model import insert_order, delete_order, order_items, get_order_id, get_orders_by_user, update_order_item_model, update_order_address_model, calculate_order_total, restore_inventory_for_order
from model.user_model import find_user_by_email
from model.inventory_model import check_id, get_inventory_item, update_inventory_quantity, get_product_name
from model.cart_model import delete_from_cart, get_cart_items_by_user
from middleman.jwt_helper import create_token, decode_token
from flask import request, jsonify
import bcrypt
import logging
from utils.mail import send_email
from utils.validators import is_valid_quantity
from middleman.jwt_helper import authorize_request
 

logger = logging.getLogger("controller_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("controller.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def confirm_order(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    address = data.get("address")
    city = data.get("city")
    country = data.get("country")
    zipcode = data.get("zipcode")
    phone_number = data.get("phone_number")

    if not all([email, password, address, city, country, zipcode, phone_number]):
        logger.warning("Order confirmation failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Order confirmation failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        logger.warning(f"Order confirmation failed: Invalid credentials ({email})")
        return jsonify({"error": "Invalid credentials"}), 401
    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    cart_items = get_cart_items_by_user(user_id)
    if not cart_items:
        logger.warning(f"Order confirmation failed: No items in cart for user ({email})")
        return jsonify({"error": "No items in cart"}), 404
    try:
        for item in cart_items:
            insert_order(
        user_id,
        item['product_id'],
        address,
        city,
        country,
        zipcode,
        phone_number
        )
            logger.info(f"Order confirmed for user {user_id}: inventory: {item['product_id']}")

            new_quantity = item["stock_quantity"] - item["quantity"]
            update_inventory_quantity(
                    item["product_id"],
                    item["product_size"],
                    item["product_color"],
                    item["product_quality"],
                    new_quantity
                )
            

            order_items(
    order_id=get_order_id(user_id, product_id=item["product_id"]),
    product_id=item["product_id"],
    quantity=item["quantity"],
    size=item["product_size"],
    color=item["product_color"],
    quality=item["product_quality"],
    product_price=item["product_price"],
    product_name=get_product_name(item["product_id"], item["product_size"], item["product_color"], item["product_quality"])
)
            
            
            delete_from_cart(item["cart_id"])
        
        logger.info(f"Order confirmed and cart cleared for user {user_id}")
        send_email(email, "✅ order placed", f"Your order {get_product_name(item["product_id"], item["product_size"], item["product_color"], item["product_quality"])} has been placed.")
        return jsonify({"message": "Order placed successfully and cart cleared"}), 200
    
    except Exception as e:
        logger.error(f"Order confirmation failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Order confirmation failed: {str(e)}"}), 500

def get_orders(request):
    data = request.get_json()
    email = data.get("email")

    if not all([email]):
        logger.warning("Order retrieval failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Order retrieval failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404
    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    total = calculate_order_total(user_id)
    logger.info(f"Total order amount for user {user_id}: {total}")

    orders = get_orders_by_user(user_id)
    if not orders:
        logger.warning(f"No orders found for user {user_id}")
        return jsonify({"orders": [], "message": "No orders found"}), 200

    logger.info(f"Orders retrieved successfully for {email}")

    return jsonify({
        "message": "Orders retrieved successfully",
        "total_amount": total,
        "orders": orders
    }), 200

    

def update_order_item(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    product_id = data.get("product_id")
    order_id = data.get("order_id")
    quantity = data.get("quantity")
    product_size = data.get("product_size")
    product_color = data.get("product_color")
    product_quality = data.get("product_quality")

    if not all([email, password, order_id, quantity, product_size, product_color, product_quality, product_id]):
        logger.warning("Order item update failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Order item update failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404    
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        logger.warning(f"Order item update failed: Invalid credentials ({email})")
        return jsonify({"error": "Invalid credentials"}), 401
    if not is_valid_quantity(quantity):
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code

    product_id = check_id(product_id)
    if not product_id:
        logger.warning(f"Order item update failed: inventory not found ({product_id})")
        return jsonify({"error": "inventory id not found"}), 404
    
    from model.order_model import get_order_item
    old_item = get_order_item(order_id, product_id)
    if not old_item:
        return jsonify({"error": "Order item not found"}), 404

    # Restore inventory for old item
    old_inventory = get_inventory_item(
        old_item["product_id"],
        old_item["product_size"],
        old_item["product_color"],
        old_item["product_quality"]
    )
    if old_inventory:
        restored_quantity = old_inventory["stock_quantity"] + old_item["quantity"]
        update_inventory_quantity(
            old_item["product_id"],
            old_item["product_size"],
            old_item["product_color"],
            old_item["product_quality"],
            restored_quantity
        )

    item = get_inventory_item(product_id, product_size, product_color, product_quality)
    if not item:
        return jsonify({"error": "Item with specified attributes not found in inventory"}), 404

    if item["stock_quantity"] < quantity:
        return jsonify({"error": "Requested quantity not available"}), 400

    new_quantity = item["stock_quantity"] - quantity

    try:
        update_order_item_model(order_id, product_id, quantity, product_size, product_color, product_quality)
        logger.info(f"Order item updated successfully for {email}")
        update_inventory_quantity(product_id, product_size, product_color, product_quality, new_quantity)
        return jsonify({"message": "Order item updated successfully"}), 200
    except Exception as e:
        logger.error(f"Order item update failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Order item update failed: {str(e)}"}), 500

def update_order_address(request):
    data = request.get_json()
    email = data.get("email")
    order_id = data.get("order_id")
    address = data.get("address")
    city = data.get("city")
    country = data.get("country")
    zipcode = data.get("zipcode")
    phone_number = data.get("phone_number")

    if not all([email, order_id, address, city, country, zipcode, phone_number]):
        logger.warning("Order address update failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Order address update failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code

    try:
        update_order_address_model(order_id, address, city, country, zipcode, phone_number)
        logger.info(f"Order address updated successfully for {email}")
        return jsonify({"message": "Order address updated successfully"}), 200
    except Exception as e:
        logger.error(f"Order address update failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Order address update failed: {str(e)}"}), 500

def delete_orders(request):
    data = request.get_json()
    email = data.get("email")
    order_id = data.get("order_id")
    if not all([email, order_id]):
        logger.warning("Order deletion failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Order deletion failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    try:
        restore_inventory_for_order(order_id)
        delete_order(order_id)
        logger.info(f"Order deleted successfully for {email}")
        return jsonify({"message": "Order deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Order deletion failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Order deletion failed: {str(e)}"}), 500