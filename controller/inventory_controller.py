from flask import request, jsonify
from model.inventory_model import fetch_all_inventory
import logging
import bcrypt
from middleman.jwt_helper import authorize_request


logger = logging.getLogger("controller_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("controller.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_inventory(request):

    decoded, user_id, error_response, status_code = authorize_request()
    if error_response:
        return error_response, status_code
    try:
        rows = fetch_all_inventory()
        logger.info(f"inventory fetched successfully for user {user_id}")
        return jsonify({"inventory": rows}), 200
    except Exception as e:
        logger.error(f"inventory fetch failed: {e}", exc_info=True)
        return jsonify({"error": f"Verification failed: {str(e)}"}), 401
    
