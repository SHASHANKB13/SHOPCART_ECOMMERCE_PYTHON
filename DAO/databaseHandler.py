import mysql.connector
import mysql
import logging

from flask import jsonify

import Controllers.constant as constants
import json


def db_engine():
    try:
        mydb = mysql.connector.connect(host=constants.DB_HOST, user=constants.DB_USER,
                                       password=constants.DB_PASSWORD,
                                       port=constants.DB_PORT,
                                       database=constants.DB_NAME)
        return mydb
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logging.error(f"Error Database connection : {str(e)}")
        return None


def fetch_user(username):
    query = "SELECT id,username, password, email, full_name FROM users WHERE username = %s;"
    try:
        cnx = db_engine()
        if cnx is None:
            return False

        cursor = cnx.cursor()
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        # print(user_data)
        return user_data

    except Exception as e:
        logging.error(f"Error occurred in fetch_user: {str(e)}")
        return []

def insert_user(username, password, email, full_name):
    query = "INSERT INTO users (username, password, email, full_name) VALUES (%s, %s, %s, %s);"
    try:
        cnx = db_engine()
        if cnx is None:
            return False

        cursor = cnx.cursor()
        cursor.execute(query, (username, password, email, full_name,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True

    except mysql.connector.Error as err:
        logging.error(f"Error occurred in insert_user: {err}")
        return False


def fetch_products():
    query = "SELECT * FROM products;"
    try:
        cnx = db_engine()
        if cnx is None:
            logging.error("Database connection failed.")
            return False

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query)
        products_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return products_data

    except Exception as e:
        logging.error(f"Error occurred in fetch_products: {str(e)}")
        return []

def fetch_product_with_id(product_id):
    query = "SELECT * FROM products WHERE id = %s;"
    try:
        cnx = db_engine()
        if cnx is None:
            logging.error("Database connection failed.")
            return False

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (product_id,))
        products_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        return products_data

    except Exception as e:
        logging.error(f"Error occurred in fetch_products: {str(e)}")
        return []

def insert_cart_item(user_id, product_id, quantity):
    query = """
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
    """
    try:
        cnx = db_engine()
        if cnx is None:
            return False

        cursor = cnx.cursor()
        cursor.execute(query, (user_id, product_id, quantity))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True

    except mysql.connector.Error as err:
        logging.error(f"Error occurred in insert_cart_item: {err}")
        return False

def fetch_cart_details(user_id):
    query = """
        SELECT
            p.id AS product_id,
            p.name,
            p.price,
            p.image,
            p.brand,
            p.category,
            c.quantity,
            (p.price * c.quantity) AS total_price
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s;
    """
    try:
        cnx = db_engine()
        if cnx is None:
            return None

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query, (user_id,))
        cart_items = cursor.fetchall()
        cursor.close()
        cnx.close()
        # print(f"cart details: {cart_items}")
        return cart_items

    except mysql.connector.Error as err:
        logging.error(f"Error in fetch_cart_details: {err}")
        return None


def decrease_or_remove_cart_item(user_id, product_id, quantity):
    try:
        cnx = db_engine()
        if cnx is None:
            return False

        cursor = cnx.cursor()

        # Step 1: Get current quantity
        select_query = """
            SELECT quantity FROM cart_items
            WHERE user_id = %s AND product_id = %s
        """
        cursor.execute(select_query, (user_id, product_id))
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            cnx.close()
            return False  # Item not found in cart

        current_quantity = result[0]
        new_quantity = current_quantity - quantity

        if new_quantity > 0:
            # Step 2: Update quantity
            update_query = """
                UPDATE cart_items
                SET quantity = %s
                WHERE user_id = %s AND product_id = %s
            """
            cursor.execute(update_query, (new_quantity, user_id, product_id))
        else:
            # Step 3: Delete the item
            delete_query = """
                DELETE FROM cart_items
                WHERE user_id = %s AND product_id = %s
            """
            cursor.execute(delete_query, (user_id, product_id))

        cnx.commit()
        cursor.close()
        cnx.close()
        return True

    except mysql.connector.Error as err:
        logging.error(f"Error in decrease_or_remove_cart_item: {err}")
        return False
