from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests

# Initialize Flask App
app = Flask(__name__)

# Set a secret key for session management (important for using `flash` and handling user sessions)
# VPAUA9QHVCN997CN - Alpha Vantage API KEY

app.secret_key = 'patepram'  # secret key



# Route for the  Welcome Page
@app.route('/')
def welcome():
    return render_template("welcome.html")


# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add logic for authentication (this is just a placeholder)
        username = request.form.get('email')
        password = request.form.get('password')

        # Assuming successful login for now
        flash("Redirecting to dashboard...", "login_success")
        return render_template('login.html', redirect=True)

    return render_template('login.html')


# Route for Account Creation Page
@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    if request.method == 'POST':
        # Account creation (placeholder for microservice that will store authenticate user)
        email = request.form.get('email')
        password = request.form.get('password')

        # Assume successful account creation for now
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
            search_results = search_stock(query)

    return render_template('dashboard.html', search_results=search_results)


# Updated Route for Stock Details Page
@app.route('/stocks')
def stock_details():
    # Get stock details for APPL ( It will be default)
    symbol = "AAPL"  # Default stock symbol
    stock_data = get_stock_data(symbol)
    time_series_data = get_time_series_data(symbol)

    competitor = "MSFT"  # Competitior stock data example
    return render_template('stock_details.html', stock=stock_data, time_series_data=time_series_data,
                           competitor=competitor)


# Alpha Vantage API ROUTING - These will be put into another microservice for separate access
@app.route('/stock/<symbol>')
def stock_page(symbol):
    stock_data = get_stock_data(symbol)
    time_series_data = get_time_series_data(symbol)

    return render_template('stock_details.html', stock_data=stock_data, time_series_data=time_series_data)

def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=VPAUA9QHVCN997CN'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def search_stock(query):
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey=VPAUA9QHVCN997CN'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('bestMatches', [])
    else:
        return []

@app.route('/search_api', methods=['GET'])
def search_api():
    query = request.args.get('query')
    if query:
        response = requests.get(f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey=YOUR_API_KEY')
        print("API Response:", response.text)  # Log the actual response text
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch data"}), 500
    return jsonify({"error": "No query provided"}), 400



def get_time_series_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey=YOUR_API_KEY'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("Time Series (Daily)", {})
    else:
        return None


# Route for logout
@app.route('/logout')
def logout():
    flash("You have been logged out.", "info")
    return redirect(url_for('welcome'))


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
