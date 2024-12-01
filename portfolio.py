# Author: Pramit Patel
# Date: 11/30/24
# Description: Handles the operations involving users financial investments from adding cash, executing trades,
# retrieving recent transactions, and the watchlist for the stocks.


from flask import Flask, request, jsonify, session
from flask_cors import CORS  # Import Flask-CORS
import os
from datetime import datetime


# Import the User model and the db instance from account_details.py
from account_details import User, Transaction, WatchList, db

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the current app context
db.init_app(app)

# Enable CORS with support for credentials
CORS(app, supports_credentials=True)

# Route to handle adding cash to portfolio
@app.route('/add_cash', methods=['POST', 'OPTIONS'])
def add_cash():
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        return jsonify({'status': 'OK'}), 200

    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')

    # Validate the request data
    if not user_id or not amount or amount <= 0:
        return jsonify({'error': 'Invalid request data'}), 400

    try:
        with app.app_context():  # Make sure db operations run within app context
            # Find the user using filter_by instead of deprecated get()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update the cash balance and available funds in the user's portfolio
            user.cash_balance += amount
            user.available_funds += amount  # Update available funds as well

            db.session.commit()

            print(f"[DEBUG] Updated cash balance for user {user_id} to {user.cash_balance}")
            print(f"[DEBUG] Updated available funds for user {user_id} to {user.available_funds}")
            return jsonify({'message': 'Cash added to portfolio successfully', 'new_cash_balance': user.cash_balance, 'new_available_funds': user.available_funds}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to update cash balance: {str(e)}")
        return jsonify({'error': 'Failed to add cash to portfolio', 'details': str(e)}), 500

# Route to get updated funds data for the user's portfolio
@app.route('/update_funds', methods=['GET'])
def update_funds():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        with app.app_context():  # Ensure the app context for database queries
            # Find the user in the database using filter_by
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Construct the portfolio data response with only the necessary fields
            portfolio_data = {
                'account_number': user.account_number,
                'cash_balance': user.cash_balance,
                'available_funds': user.available_funds,
                'total_value': user.total_value,
                'market_value': user.market_value,
                'day_change': user.day_change,
                'gains_loss': user.gains_loss
            }

            return jsonify(portfolio_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch portfolio', 'details': str(e)}), 500


# Route to execute trade
@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    data = request.get_json()
    user_id = data.get('user_id')
    action = data.get('action')
    quantity = data.get('quantity')
    price = data.get('price')
    stock_symbol = data.get('stock_symbol')  # Corrected line to explicitly extract stock_symbol

    if not user_id or not stock_symbol or not action or not quantity or not price:
        return jsonify({'error': 'Invalid request data'}), 400

    try:
        with app.app_context():  # Make sure db operations run within app context
            # Find the user
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            total_cost = quantity * price
            transaction_fee = 4.95
            exchange_fee = 1.20
            total_fees = transaction_fee + exchange_fee
            final_cost = total_cost + total_fees if action == 'buy' else total_cost - total_fees

            if action == 'buy':
                if user.available_funds < final_cost:
                    return jsonify({'error': 'Insufficient funds'}), 400
                # Update user's available funds and total value
                user.available_funds -= final_cost
                user.total_value += total_cost

            elif action == 'sell':
                # Assuming you are tracking stock holdings (need to implement holdings tracking)
                user.available_funds += final_cost
                user.total_value -= total_cost

            # Add the transaction record
            print(f"[DEBUG] Adding transaction for user {user_id}")
            new_transaction = Transaction(
                user_id=user.id,
                stock_symbol=stock_symbol,  # Corrected to add stock_symbol to the transaction
                action=action,
                quantity=quantity,
                price=price,
                total_value=total_cost,
                date=datetime.utcnow()
            )
            db.session.add(new_transaction)
            db.session.commit()
            print(f"[DEBUG] Transaction added successfully for user {user_id}")

            return jsonify({'message': 'Trade executed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to execute trade: {str(e)}")  # Print the error message for debugging
        return jsonify({'error': f'Failed to execute trade: {str(e)}'}), 500

# Route to handle adding a transaction (buy/sell)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    user_id = data.get('user_id')
    stock_symbol = data.get('stock_symbol')
    action = data.get('action')
    quantity = data.get('quantity')
    price = data.get('price')

    if not all([user_id, stock_symbol, action, quantity, price]):
        return jsonify({'error': 'Invalid request data'}), 400

    try:
        with app.app_context():
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Calculate total value of the transaction
            total_value = float(quantity) * float(price)

            # Create a new transaction record
            new_transaction = Transaction(
                user_id=user.id,
                stock_symbol=stock_symbol,
                action=action,
                quantity=quantity,
                price=price,
                total_value=total_value,
                date=datetime.utcnow()
            )

            db.session.add(new_transaction)

            # Update user's available funds if buying or selling
            if action.lower() == 'buy':
                if user.available_funds < total_value:
                    return jsonify({'error': 'Insufficient funds'}), 400
                user.available_funds -= total_value
            elif action.lower() == 'sell':
                user.available_funds += total_value

            db.session.commit()

            return jsonify({'message': 'Transaction added successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add transaction', 'details': str(e)}), 500


# Route to get recent transactions for a user
@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        with app.app_context():
            # Fetch recent transactions from the database
            transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(10).all()

            transaction_list = [
                {
                    'stock_symbol': transaction.stock_symbol,
                    'action': transaction.action,
                    'quantity': transaction.quantity,
                    'price': transaction.price,
                    'total_value': transaction.total_value,
                    'date': transaction.date.strftime("%Y-%m-%d %H:%M:%S")
                }
                for transaction in transactions
            ]

            return jsonify(transaction_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch transactions', 'details': str(e)}), 500


# Add Stock to Watchlist
@app.route('/add_to_watchlist', methods=['POST'])
def add_to_watchlist():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    stock_symbol = data.get('stock_symbol')
    target_price = data.get('target_price')
    alert_duration = data.get('alert_duration')

    if not stock_symbol or not target_price or not alert_duration:
        return jsonify({'error': 'Invalid data provided'}), 400

    try:
        new_watchlist_item = WatchList(
            user_id=user_id,
            stock_symbol=stock_symbol,
            target_price=target_price,
            alert_duration=alert_duration,
            alert_set_date=datetime.utcnow()
        )
        db.session.add(new_watchlist_item)
        db.session.commit()

        return jsonify({'message': 'Stock added to watchlist successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add stock to watchlist: {str(e)}'}), 500

# Get User Watchlist
@app.route('/get_watchlist', methods=['GET'])
def get_watchlist():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']

    try:
        watchlist_items = WatchList.query.filter_by(user_id=user_id).all()
        watchlist_data = [
            {
                'stock_symbol': item.stock_symbol,
                'target_price': item.target_price,
                'alert_set_date': item.alert_set_date.strftime("%Y-%m-%d"),
                'alert_duration': item.alert_duration
            }
            for item in watchlist_items
        ]
        return jsonify(watchlist_data), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch watchlist: {str(e)}'}), 500

# Remove Stock from Watchlist
@app.route('/remove_from_watchlist/<string:stock_symbol>', methods=['DELETE'])
def remove_from_watchlist(stock_symbol):
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user_id = session['user_id']

    try:
        watchlist_item = WatchList.query.filter_by(user_id=user_id, stock_symbol=stock_symbol).first()
        if not watchlist_item:
            return jsonify({'error': 'Stock not found in watchlist'}), 404

        db.session.delete(watchlist_item)
        db.session.commit()

        return jsonify({'message': 'Stock removed from watchlist successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove stock from watchlist: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)