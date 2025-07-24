from flask import request, jsonify
import bcrypt
import logging
from model.user_model import find_user_by_email
from model.inventory_model import check_id, get_inventory_item
from middleman.jwt_helper import authorize_request
from model.cart_model import add_to_cart, get_cart_items, update_to_cart, delete_from_cart, is_valid_cart_id
from utils.validators import is_valid_quantity

logger = logging.getLogger("controller_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("controller.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def add_product(request):
    data = request.get_json()
    email = data.get("email")
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    product_size = data.get("product_size")
    product_color = data.get("product_color")
    product_quality = data.get("product_quality")

    

    if not all([email, product_id, quantity, product_size, product_color, product_quality]):
        logger.warning("Add product failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    
    user = find_user_by_email(email)
    if not user:
        logger.warning(f"User sign-in failed: User not found ({email})")
        return {"error": "User not found"}, 404
    
    product_id = check_id(product_id)
    if not product_id:
        logger.warning(f"Order creation failed: inventory not found ({ product_id })")
        return jsonify({"error": "product id not found"}), 404
    
    if not is_valid_quantity(quantity):
        logger.warning(f"Add product failed: Invalid quantity ({quantity})")
        return jsonify({"error": "Quantity must be a positive integer"}), 400
    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    item = get_inventory_item(product_id, product_size, product_color, product_quality)
    if not item:
        return jsonify({"error": "Item with specified attributes not found in inventory"}), 404

    if item["stock_quantity"] < quantity:
        return jsonify({"error": "Requested quantity not available"}), 400
    

    add_to_cart(user_id, product_id, quantity, product_size, product_color, product_quality, stock_quantity=item["stock_quantity"], product_price=item["product_price"])
    logger.info(f"Product added to cart for {email}: {product_id} with quantity {quantity}")



    return jsonify({"message": "Product added to cart"}), 200


def get_cart(request):
    data = request.get_json()
    email = data.get("email")

    if not all([email]):
        logger.warning("Cart fetch failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400

    user = find_user_by_email(email)
    if not user:
        logger.warning(f"Cart fetch failed: User not found ({email})")
        return jsonify({"error": "User not found"}), 404

    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    try:
        rows = get_cart_items()
        logger.info(f"Cart fetched for {email}")
        return jsonify({"cart": rows}), 200
    except Exception as e:
        logger.error(f"Cart fetch failed for {email}: {e}", exc_info=True)
        return jsonify({"error": f"Cart fetch failed: {str(e)}"}), 401
    
def update_cart(request):
    data = request.get_json()
    cart_id = data.get("cart_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    product_size = data.get("product_size")
    product_color = data.get("product_color")
    product_quality = data.get("product_quality")


    if not all([cart_id, product_id]):
        logger.warning("Cart update failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400
    
    
    product_id = check_id(product_id)
    if not product_id:
        logger.warning(f"Cart update failed: product not found ({product_id})")
        return jsonify({"error": "product id not found"}), 404
    
    if not is_valid_cart_id(cart_id):
        logger.warning(f"Cart update failed: Invalid cart ID ({cart_id})")
        return jsonify({"error": "Invalid cart ID"}), 404
    
    if not is_valid_quantity(quantity):
        logger.warning(f"Add product failed: Invalid quantity ({quantity})")
        return jsonify({"error": "Quantity must be a positive integer"}), 400
    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    item = get_inventory_item(product_id, product_size, product_color, product_quality)
    if not item:
        return jsonify({"error": "Item with specified attributes not found in inventory"}), 404

    if item["stock_quantity"] < quantity:
        return jsonify({"error": "Requested quantity not available"}), 400

    update_to_cart(product_id, quantity, product_size, product_color, product_quality, cart_id)

    return jsonify({"message": "Product added to cart and inventory updated"}), 200

def delete_cart_item(request):
    data = request.get_json()
    cart_id= data.get("cart_id")
    if not all([cart_id]):
        logger.warning("Cart deletion failed: Missing fields")
        return jsonify({"error": "Missing fields"}), 400

    
    if not is_valid_cart_id(cart_id):
        logger.warning(f"Cart deletion failed: Invalid cart ID ({cart_id})")
        return jsonify({"error": "Invalid cart ID"}), 404
    
    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    
    try:
        delete_from_cart(cart_id)
        logger.info(f"Cart item deleted for {cart_id}")
        return jsonify({"message": "Item deleted from cart"}), 200
    except Exception as e:
        logger.error(f"Cart deletion failed for {cart_id}: {e}", exc_info=True)
        return jsonify({"error": f"Cart deletion failed: {str(e)}"}), 401