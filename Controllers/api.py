from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import DAO.databaseHandler as dbh
import re
import logging

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Validate user
    user = dbh.fetch_user(username)
    if user and check_password_hash(user[2], password):
        return jsonify({"message": "Login successful", "data": {"user_id":user[0], "username": user[1], "email": user[3]}}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    fullname = data.get('fullname')
    if not username or not password or not email or not fullname:
        return jsonify({"error": "All fields are required"}), 400

    # Regex: 8+ chars, 1 lowercase, 1 uppercase, 1 digit, 1 special char
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    if not re.match(password_regex, password):
        return jsonify({
            "error": "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character."
        }), 400

    # Check if username already exists
    if dbh.fetch_user(username):
        return jsonify({"error": "Username already exists"}), 409

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    # Insert user into the database
    dbh.insert_user(username, hashed_password, email, fullname)

    return jsonify({"message": "User registration successful"}), 201


@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = dbh.fetch_products()
        return jsonify({"message": "fetched products successfully", "data": {"products":products}}), 200
    except Exception as e:
        logging.error(f"An error occurred getting products : {str(e)}")
        return jsonify({"message":f"An error occurred getting products: {str(e)}"})

@app.route('/api/product/details/<id>', methods=['GET'])
def get_product_details(id):
    try:
        product_details = dbh.fetch_product_with_id(product_id=id)

        return jsonify({"message": "fetched product details successfully", "data": product_details}), 200
    except Exception as e:
        logging.error(f"An error occurred getting product details : {str(e)}")
        return jsonify({"message":f"An error occurred getting product details: {str(e)}"})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)  # Default quantity to 1 if not provided

        if not user_id or not product_id:
            return jsonify({"error": "user_id and product_id are required"}), 400

        cart_add = dbh.insert_cart_item(user_id, product_id, quantity)

        if cart_add:
            return jsonify({
                "message": "Product added to cart successfully",
                "data": {
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity
                }
            }), 200
        else:
            return jsonify({"error": "Failed to add product to cart"}), 500

    except Exception as e:
        logging.error(f"Exception in /api/cart/add: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/cart/details/<user_id>', methods=['GET'])
def get_user_cart_details(user_id):
    try:
        # Fetch cart details from the DB helper
        user_cart_details = dbh.fetch_cart_details(user_id=user_id)
        cart_count = len(user_cart_details) if user_cart_details else 0

        return jsonify({
            "message": "Fetched cart details successfully",
            "data": {
                "products": user_cart_details,
                "count": cart_count
            }
        }), 200

    except Exception as e:
        logging.error(f"An error occurred getting cart details: {str(e)}")
        return jsonify({
            "message": f"An error occurred getting cart details: {str(e)}"
        }), 500


@app.route('/api/cart/remove', methods=['POST'])
def remove_cart_items():
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)  # Default quantity to 1 if not provided

        if not user_id or not product_id:
            return jsonify({"error": "user_id and product_id are required"}), 400

        cart_add = dbh.decrease_or_remove_cart_item(user_id, product_id, quantity)

        if cart_add:
            return jsonify({
                "message": "Product removed from cart successfully",
                "data": {
                    "user_id": user_id,
                    "product_id": product_id,
                    "quantity": quantity
                }
            }), 200
        else:
            return jsonify({"error": "Failed to remove product from cart"}), 500

    except Exception as e:
        logging.error(f"Exception in /api/cart/remove: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
