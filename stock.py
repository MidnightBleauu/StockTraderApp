# Author: Pramit Patel
# Date: 11/30/24
# Description: Handles the API requests for the stocks data pulled using ALPHA Vantage API, and allows for stock ticker
# stock search, earnings report, and other financial data

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

# Create a Flask app instance for the stock microservice
app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app)

# Alpha Vantage API Key - (Premium Key, this will be blank before uploaded to github)
Alpha_Vantage_Key = '' # obtain a free key from Alpha Vantage

# Function to get stock data from Alpha Vantage
def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def get_time_series_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Time Series (Daily)" in data:
            print(f"Time Series Data for {symbol}: {data['Time Series (Daily)']}")
            return data
        elif "Error Message" in data:
            print(f"Error fetching time series data for {symbol}: {data['Error Message']}")
        else:
            print(f"Unexpected response structure for time series data for {symbol}: {data}")
    else:
        print(f"Error fetching time series data for {symbol}: {response.status_code}")
    return {}

# Function to get income statement data from Alpha Vantage
def get_income_statement_data(symbol):
    url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Debug output
        print("Income Statement Response:", data)
        return data if "annualReports" in data else {}
    else:
        print(f"Error: Failed to fetch income statement for {symbol}. Status code: {response.status_code}")
        return {}

# Function to get earnings data from Alpha Vantage
def get_earnings_data(symbol):
    url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}


# Function to get the current stock price
def get_current_price(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Time Series (Daily)" in data:
            latest_date = max(data["Time Series (Daily)"].keys())  # Get the most recent date
            latest_data = data["Time Series (Daily)"][latest_date]
            return latest_data["4. close"]  # Return the latest closing price as the current price
        else:
            return "N/A"  # If data is not available
    else:
        return "N/A"


def get_news_sentiment():
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error": "Failed to fetch news sentiment data"}

# Function to get top gainers, losers, and most active tickers
def get_top_gainers_losers():
    url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error": "Failed to fetch top gainers/losers"}

def get_analytics_fixed_window(symbols, range_start, range_end, interval, calculations):
    symbols_str = ",".join(symbols)
    url = f"https://www.alphavantage.co/query?function=ANALYTICS_FIXED_WINDOW&SYMBOLS={symbols_str}&RANGE={range_start}&RANGE={range_end}&INTERVAL={interval}&OHLC=close&CALCULATIONS={calculations}&apikey={Alpha_Vantage_Key}"
    print(f"Requesting analytics data from: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except ValueError:
            print("Invalid JSON response received")
            return {}
    else:
        print(f"Error fetching analytics data for {symbols}: {response.status_code}, Response: {response.text}")
        return {}


def get_cash_flow_data(symbol):
    url = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={Alpha_Vantage_Key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# Route for fetching stock details
@app.route('/stock_details', defaults={'symbol': 'AAPL'})
@app.route('/stock_details/<symbol>')
def stock_details(symbol):
    try:
        # Get stock details for the specified symbol
        stock_data = get_stock_data(symbol)
        time_series_data = get_time_series_data(symbol)
        income_statement = get_income_statement_data(symbol)
        earnings_data = get_earnings_data(symbol)
        current_price = get_current_price(symbol)
        cash_flow_data = get_cash_flow_data(symbol)


        # Fetch analytics data using the Advanced Analytics (Fixed Window) API endpoint
        analytics_data = get_analytics_fixed_window(
            symbols=[symbol],
            range_start="2023-07-01",
            range_end="2023-08-31",
            interval="DAILY",
            calculations="MEAN,STDDEV,CUMULATIVE_RETURN"
        )

        # Combine all data
        combined_data = {
            'stock_data': stock_data,
            'time_series_data': time_series_data,
            'income_statement': income_statement,
            'earnings_data': earnings_data,
            'current_price': current_price,
            'cash_flow_data': cash_flow_data,
            'analytics_data': analytics_data if analytics_data else {"message": "Analytics data not available"}
        }

        return jsonify(combined_data)

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# Route for stock search suggestions
@app.route('/search_api', methods=['GET'])
def search_api():
    # This endpoint makes an API call for stock symbol suggestions
    query = request.args.get('query')
    if query:
        url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={Alpha_Vantage_Key}'
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch data"}), 500
    return jsonify({"error": "No query provided"}), 400


@app.route('/news_sentiment')
def news_sentiment():
    news_data = get_news_sentiment()
    return jsonify(news_data)

@app.route('/top_gainers_losers')
def top_gainers_losers():
    gainers_losers_data = get_top_gainers_losers()
    return jsonify(gainers_losers_data)


# Run the Flask application
if __name__ == '__main__':
    app.run(port=5001)  # Running this microservice on a different port (e.g., 5001)