# Author: Pramit Patel
# Date: 11/30/24
# Description: Creates the intial database with SQLAlchemy to store user data and financial data

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Ininitalize flask to set up database
app = Flask(__name__)

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQL database
db = SQLAlchemy(app)

# User Database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)
    cash_balance = db.Column(db.Float, default=0.0)
    available_funds = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    market_value = db.Column(db.Float, default=0.0)
    day_change = db.Column(db.Float, default=0.0)
    gains_loss = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

# Transaction Database
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# WatchList Database
class WatchList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    alert_set_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    alert_duration = db.Column(db.Integer, nullable=False)  # Duration in days


# Runs to create the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")