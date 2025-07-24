from controller.user_controller import signup, signin, updateuser, sendotp, verify_otp
from controller.inventory_controller import get_inventory
from controller.order_controller import delete_orders, confirm_order, get_orders, update_order_item, update_order_address
from flask import request
import logging
from controller.cart_controller import add_product, get_cart, update_cart, delete_cart_item

logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/auth/register', methods=['POST'])
    def otp_route():
        logger.info("Signup route accessed")
        return signup(request)
    
    @app.route('/auth/login', methods=['POST'])
    def login_route():
        logger.info("Signin route accessed")
        return signin(request)
    
    @app.route('/auth/update-user', methods=['PUT'])
    def update_users_route():
        logger.info("update route accessed")
        return updateuser(request)
    
    @app.route('/auth/get-otp', methods=['POST'])
    def otp_users_route():
        logger.info("otp route accessed")
        return sendotp(request)
    
    @app.route('/auth/verify-otp', methods=['POST'])
    def verify_users_route():
        logger.info("verify route accessed")
        return verify_otp(request)

    @app.route('/inventory', methods=['GET'])
    def get_inventory_route():
        logger.info("inventory route accessed")
        return get_inventory(request)

    @app.route('/cart/add', methods=['POST'])
    def add_product_route():
        logger.info("Add Product route accessed")
        return add_product(request)
    
    @app.route('/cart/show', methods=['GET'])
    def get_cart_route():
        logger.info("Get Cart route accessed")
        return get_cart(request)
    
    @app.route('/cart/update', methods=['PUT'])
    def update_cart_route():
        logger.info("Update Cart route accessed")
        return update_cart(request)
    
    @app.route('/cart/delete', methods=['DELETE'])
    def delete_cart_route():
        logger.info("Delete Cart route accessed")
        return delete_cart_item(request)
    
    @app.route('/order/confirm', methods=['POST'])
    def create_order_route():
        logger.info("Create Order route accessed")
        return confirm_order(request)

    @app.route('/order/update/item', methods=['PUT'])
    def update_order_item_route():
        logger.info("Update Order Item route accessed")
        return update_order_item(request)

    @app.route('/order/update/address', methods=['PUT'])
    def update_order_address_route():
        logger.info("Update Order Address route accessed")
        return update_order_address(request)
    
    @app.route('/order/show', methods=['GET'])
    def get_orders_route(): 
        logger.info("GET Order route accessed")
        return get_orders(request)
    
    @app.route('/order/delete', methods=['DELETE'])
    def delete_orders_route():
        logger.info("Delete Order route accessed")
        return delete_orders(request)