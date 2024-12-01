# Author: Pramit Patel
# Date: 11/30/24
# Description: Main entry point for the web application, handling route definitions for login, auth,
# account creation, dashboard, stock page, and routing through the application

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests

# Initialize Flask App
app = Flask(__name__)

# Set a secret key for session management (important for using `flash` and handling user sessions)
app.secret_key = ''

# Link to microservice URLs
STOCK_SERVICE_BASE_URL = "http://localhost:5001"
ACCOUNTS_SERVICE_BASE_URL = "http://localhost:5004"
PORTFOLIO_SERVICE_BASE_URL = "http://localhost:5006"

# Route for the Welcome Page
@app.route('/')
def welcome():
    return render_template("welcome.html")

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Send request to accounts microservice to verify credentials
        try:
            response = requests.post(
                f"{ACCOUNTS_SERVICE_BASE_URL}/login",
                json={'email': email, 'password': password}
            )

            if response.status_code == 200:
                user_data = response.json()

                # Check if the response contains 'user_id' key
                if 'user_id' in user_data:
                    session['user_id'] = user_data['user_id']
                    flash("Logged in successfully!", "login_success")
                    return redirect(url_for('dashboard'))
                else:
                    flash('Login response missing user_id.', 'error')

            else:
                # Handle specific error messages returned by the accounts service
                try:
                    error_message = response.json().get('error', 'Invalid login credentials')
                    flash(error_message, "error")
                except ValueError:
                    flash('Invalid login credentials', "error")
        except requests.exceptions.RequestException as e:
            flash(f"Failed to connect to the login service: {e}", "error")

    return render_template('login.html')

# Route for Account Creation
@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    if request.method == 'POST':
        # Gather form data
        name = request.form.get('first_name') + " " + request.form.get('last_name')
        email = request.form.get('email')
        confirm_email = request.form.get('confirm_email')
        password = request.form.get('password')
        confirm_password = request.form.get('password_repeat')

        # Ensure emails match
        if email != confirm_email:
            flash("Emails do not match.", "error")
            return render_template('account_creation.html')

        # Send request to create an account in accounts microservice
        try:
            response = requests.post(
                f"{ACCOUNTS_SERVICE_BASE_URL}/create_account",
                json={
                    'name': name,
                    'email': email,
                    'password': password,
                    'confirm_password': confirm_password
                }
            )

            if response.status_code == 200:
                # Extract the redirect URL from the response
                redirect_url = response.json().get('redirect_url', '/dashboard')
                flash("Account created successfully! Redirecting to dashboard...", "success")
                return redirect(redirect_url)
            else:
                try:
                    flash(response.json().get('error', 'Failed to create account'), "error")
                except ValueError:
                    flash('Failed to create account', "error")
        except requests.exceptions.RequestException as e:
            flash(f"Failed to connect to the account creation service: {e}", "error")

    return render_template('account_creation.html')

# Route for Dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch updated portfolio data from portfolio microservice
    try:
        response = requests.get(f"{PORTFOLIO_SERVICE_BASE_URL}/update_funds?user_id={user_id}")
        if response.status_code == 200:
            portfolio_data = response.json()
        else:
            flash("Failed to fetch portfolio data.", "error")
            portfolio_data = {
                'account_number': 'N/A', 'cash_balance': 0, 'available_funds': 0, 'total_value': 0,
                'market_value': 0, 'day_change': 0, 'gains_loss': 0
            }

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Portfolio Request Exception: {e}")
        flash("Failed to connect to the portfolio service.", "error")
        portfolio_data = {
            'account_number': 'N/A', 'cash_balance': 0, 'available_funds': 0, 'total_value': 0,
            'market_value': 0, 'day_change': 0, 'gains_loss': 0
        }

    # Fetch recent transactions for the user
    try:
        transactions_response = requests.get(f"{PORTFOLIO_SERVICE_BASE_URL}/get_transactions?user_id={user_id}")
        if transactions_response.status_code == 200:
            transactions = transactions_response.json()
        else:
            transactions = []
            flash("Failed to fetch recent transactions.", "error")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Transactions Request Exception: {e}")
        transactions = []
        flash("Failed to connect to the transactions service.", "error")

    # Render the dashboard with the portfolio data and transactions
    return render_template(
        'dashboard.html',
        user_id=user_id,  # Pass user_id to the template
        account_number=portfolio_data.get('account_number', 'N/A'),
        cash_balance=portfolio_data.get('cash_balance', 0),
        available_funds=portfolio_data.get('available_funds', 0),
        total_value=portfolio_data.get('total_value', 0),
        market_value=portfolio_data.get('market_value', 0),
        day_change=portfolio_data.get('day_change', 0),
        gains_loss=portfolio_data.get('gains_loss', 0),
        transactions=transactions  # Pass the transactions to the template
    )

# Route for fetching stock details
@app.route('/stocks', defaults={'symbol': 'AAPL'})
@app.route('/stocks/<symbol>')
def stock_details(symbol):
    # Make a request to the stock microservice to get stock details
    try:
        response = requests.get(f"{STOCK_SERVICE_BASE_URL}/stock_details/{symbol}")
        if response.status_code == 200:
            stock_data = response.json()
        else:
            flash("Failed to fetch stock data.", "error")
            stock_data = {
                'stock_data': {},
                'time_series_data': {},
                'income_statement': {},
                'earnings_data': {},
                'current_price': 'N/A'
            }
    except requests.exceptions.RequestException as e:
        # In case of connection error or timeout
        flash("Could not connect to the stock service.", "error")
        stock_data = {
            'stock_data': {},
            'time_series_data': {},
            'income_statement': {},
            'earnings_data': {},
            'current_price': 'N/A'
        }

    return render_template(
        'stock_details.html',
        stock=stock_data.get('stock_data', {}),
        time_series_data=stock_data.get('time_series_data', {}),
        income_statement=stock_data.get('income_statement', {}),
        earnings_data=stock_data.get('earnings_data', {}),
        current_price=stock_data.get('current_price', 'N/A'),
        analytics_data=stock_data.get('analytics_data', {})
    )

# Route to handle adding funds via form submission
@app.route('/add_funds', methods=['POST'])
def add_funds():
    if 'user_id' not in session:
        flash("Please log in to add funds.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    amount = request.form.get('amount')

    # Validate amount
    if not amount or float(amount) <= 0:
        flash("Invalid amount provided.", "error")
        return redirect(url_for('account_settings'))

    # Send request to portfolio microservice to add cash
    try:
        response = requests.post(
            f"{PORTFOLIO_SERVICE_BASE_URL}/add_cash",
            json={
                'user_id': user_id,
                'amount': float(amount)
            }
        )

        if response.status_code == 200:
            flash("Funds added successfully!", "success")
        else:
            try:
                flash(response.json().get('error', 'Failed to add funds'), "error")
            except ValueError:
                flash("Failed to add funds", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Failed to connect to the portfolio service: {e}", "error")

    # Redirect to dashboard to view updated balance
    return redirect(url_for('dashboard'))

# Route for summary Page
@app.route('/summary')
def summary():
    try:
        # Requesting news sentiment data from the stock microservice
        news_response = requests.get(f"{STOCK_SERVICE_BASE_URL}/news_sentiment")
        if news_response.status_code == 200:
            news_sentiment = news_response.json()
        else:
            news_sentiment = {}
            flash("Failed to fetch news sentiment.", "error")

        gainers_losers_response = requests.get(f"{STOCK_SERVICE_BASE_URL}/top_gainers_losers")
        if gainers_losers_response.status_code == 200:
            top_gainers_losers = gainers_losers_response.json()
        else:
            top_gainers_losers = {}
            flash("Failed to fetch top gainers/losers.", "error")

    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        news_sentiment = {}
        top_gainers_losers = {}
        flash("Failed to fetch market data.", "error")

    return render_template('summary.html', news_sentiment=news_sentiment, top_gainers_losers=top_gainers_losers)

# Route for updating user information (Settings Page)
@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if 'user_id' not in session:
        flash("Please log in to access account settings.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get data from the form
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        address = request.form.get('address')
        current_password = request.form.get('password')

        # Send request to accounts microservice
        response = requests.post(
            f"{ACCOUNTS_SERVICE_BASE_URL}/update_user",
            json={
                'user_id': session['user_id'],
                'name': name,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'current_password': current_password
            }
        )

        if response.status_code == 200:
            flash("User information updated successfully!", "success")
        else:
            try:
                flash(response.json().get('error', 'Failed to update user information'), "error")
            except ValueError:
                flash("Failed to update user information", "error")

    return render_template('account_settings.html')


# Route to get portfolio details for a user
@app.route('/get_portfolio', methods=['GET'])
def get_portfolio():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Find the user in the database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Construct the portfolio data response
        portfolio_data = {
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    user_id = session['user_id']
    data = request.get_json()
    action = data.get('action')
    quantity = data.get('quantity')
    price = data.get('price')
    stock_symbol = data.get('stock_symbol')  # Extract stock_symbol from request


    if not action or not quantity or not price:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    try:
        # Send request to portfolio microservice to execute the trade
        response = requests.post(
            f"{PORTFOLIO_SERVICE_BASE_URL}/execute_trade",
            json={
                'user_id': user_id,
                'stock_symbol': stock_symbol,
                'action': action,
                'quantity': quantity,
                'price': price
            }
        )

        if response.status_code == 200:
            return jsonify({'success': True}), 200
        else:
            error_message = response.json().get('error', 'Failed to execute trade')
            return jsonify({'success': False, 'error': error_message}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f"Failed to connect to the trade service: {e}"}), 500

# Route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('welcome'))

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)