# Author: Pramit Patel
# Date: 11/30/24
# Description: Handles the user information & authentification , storage of user data
# into the accounts database for storage,

from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
import os
import random
import logging

# Import the User model and the db instance from account_details.py
from account_details import User, db

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))  # Use environment variable for secret key

# Configure app for the shared database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Initialize SQLAlchemy with the current app context
db.init_app(app)

# Create tables if they do not exist
with app.app_context():
    db.create_all()

# Route to create a new account
@app.route('/create_account', methods=['POST'])
def create_account():
    with app.app_context():  # Ensure the app context for any DB operation
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Validation
        if not name or not email or not password or not confirm_password:
            return jsonify({'error': 'All fields are required'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Account with this email already exists'}), 400

        # Generate unique account number
        account_number = str(random.randint(1000000000, 9999999999))

        # Hash password and create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            account_number=account_number,
            name=name,
            email=email,
            password=hashed_password,
        )

        try:
            db.session.add(new_user)
            db.session.commit()

            # Automatically log the user in by storing user_id in the session
            session['user_id'] = new_user.id

            logging.info(f"Account created for user ID: {new_user.id}, email: {email}")

            return jsonify({'message': 'Account created successfully', 'redirect_url': '/dashboard'}), 200
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create account: {str(e)}")
            return jsonify({'error': 'Failed to create account', 'details': str(e)}), 500

# Route to login
@app.route('/login', methods=['POST'])
def login():
    with app.app_context():  # Ensure app context for DB operations
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        logging.info(f"Attempting login for email: {email}")

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            logging.warning(f"Login failed for email {email}: User not found")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check password using bcrypt
        if not bcrypt.check_password_hash(user.password, password):
            logging.warning(f"Login failed for email {email}: Incorrect password")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Set session for successful login
        session['user_id'] = user.id
        logging.info(f"Login successful for email: {email}, user_id: {user.id}")

        return jsonify({'user_id': user.id, 'message': 'Logged in successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)