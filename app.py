from flask import Flask, render_template, request, redirect, url_for, flash
import requests

# Initialize Flask App
app = Flask(__name__)

# Set a secret key for session management (important for using `flash` and handling user sessions)
app.secret_key = 'patepram'

# Link to microservice stock.py
STOCK_SERVICE_BASE_URL = "http://localhost:5001"

# Route for the Welcome Page
@app.route('/')
def welcome():
    return render_template("welcome.html")

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        flash("Redirecting to dashboard...", "login_success")
        return render_template('login.html', redirect=True)
    return render_template('login.html')

# Route for Account Creation Page
@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('account_creation.html')

# Route for Dashboard Pages
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    search_results = None
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            # You can implement your search logic here
            search_results = []  # Placeholder for search results
    return render_template('dashboard.html', search_results=search_results)


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

# Route for summary Page
@app.route('/summary')
def summary():
    try:
        # Requesting news sentiment data from the stock microservice
        news_response = requests.get(f"{STOCK_SERVICE_BASE_URL}/news_sentiment")
        if news_response.status_code == 200:
            news_sentiment = news_response.json()
            print("News Sentiment Data:", news_sentiment)  # For debugging to make sure it all works
        else:
            news_sentiment = {}
            print("Failed to fetch news sentiment, Status Code:", news_response.status_code)

        gainers_losers_response = requests.get(f"{STOCK_SERVICE_BASE_URL}/top_gainers_losers")
        if gainers_losers_response.status_code == 200:
            top_gainers_losers = gainers_losers_response.json()
            print("Top Gainers/Losers Data:", top_gainers_losers)
        else:
            top_gainers_losers = {}
            print("Failed to fetch top gainers/losers, Status Code:", gainers_losers_response.status_code)

    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        news_sentiment = {}
        top_gainers_losers = {}
        flash("Failed to fetch market data.", "error")

    return render_template('summary.html', news_sentiment=news_sentiment, top_gainers_losers=top_gainers_losers)


# Route for logout
@app.route('/logout')
def logout():
    flash("You have been logged out.", "info")
    return redirect(url_for('welcome'))

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)