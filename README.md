# StockTraderApp

Stock Trader App with separate microservices - Stock Searching with API connection to Alpha Vantage/NASDAQ, User Authentication, User Notifications, and Portfolio Storage.

---

## Features

- **Real-Time Stock Data**: Fetches live stock prices, trends, and company information.
- **Account Management**: Securely manages user login, profile updates, and financial transactions.
- **Portfolio Tracking**: Displays owned stocks, tracks gains/losses, and shows historical performance.
- **Notifications**: Sends alerts about stock price changes or account updates.

---

## Microservices Architecture

This app uses a modular microservices architecture. Each microservice runs independently and communicates with the Main Program via REST APIs.

### Microservices Overview

| **Microservice**    | **File**           | **Language**     | **Responsibility**                                                                                 |
|----------------------|--------------------|------------------|---------------------------------------------------------------------------------------------------|
| **Microservice A**  | `notif.py`         | Python           | Sends real-time notifications about stock changes or account activities (provided by teammate).    |
| **Microservice B**  | `stock.py`         | Python           | Fetches real-time stock data, trends, and company details using the Alpha Vantage API.             |
| **Microservice C**  | `account.py`       | Python           | Handles user authentication, account details, and adding funds securely.                           |
| **Microservice D**  | `portfolio.py`     | Python           | Manages portfolio data, tracks stock holdings, and calculates gains/losses.                        |
| **Main Program**    | `app.py`           | Python           | Acts as the central controller, communicating with all microservices via REST APIs.                |

---

## Technologies Used

- **Programming Language**: Python
- **APIs**: Alpha Vantage for stock data
- **Database**: MongoDB for storing user and account data
- **Frameworks/Libraries**: 
  - `Flask`: For building REST APIs.
  - `SQLAlchemy`: For database modeling.
  - `pymongo`: For MongoDB interactions.

---
